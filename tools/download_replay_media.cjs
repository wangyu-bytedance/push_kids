// Read-only COS download using the already authenticated wxcloud CLI session.
// Input/output paths belong to a private TemporaryDirectory, never the repository.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
let phase = 'configuration';
let downloaded = 0;
const credentials = new Map();
async function main() {
  const root = process.env.PUSH_KIDS_WXCLOUD_CLI_ROOT;
  if (!root) throw new Error('cli_root_missing');
  require(path.join(root, 'lib/utils/log')).logger.debug = () => {};
  require(path.join(root, 'node_modules/axios')).default.defaults.timeout = 15000;
  require(path.join(root, 'lib/api/common')).setApiCommonParameters({region: 'ap-shanghai'});
  phase = 'environment';
  const envs = await require(path.join(root, 'lib/api')).DescribeWxCloudBaseRunEnvs({});
  const rows = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const COS = require(path.join(root, 'node_modules/cos-nodejs-sdk-v5'));
  for (const row of rows) {
    const storage = envs.EnvList.flatMap(e => e.Storages || []).find(
      s => row.ref.startsWith('cloud://') && row.ref.split('/')[2].endsWith(s.Bucket));
    phase = 'scope';
    if (!storage || row.bytes > 10 * 1024 * 1024) throw new Error('media_scope');
    phase = 'credentials';
    // CLI 2.3.3 posts this endpoint, which returns only base_resp. The endpoint
    // accepts the same read-only credential request as GET query parameters.
    let credential = credentials.get(storage.Bucket);
    if (!credential) credential = await require(path.join(root, 'lib/api/base')).fetchApi(
      'wxa-dev-qbase/gettcbtoken', {}, {method:'GET', params:{region:storage.Region,
        source:storage.Bucket,scene:'TOKEN_SCENE_COS',service:'cos'}});
    if (!credential?.secretid || !credential?.secretkey || !credential?.token) {
      process.stderr.write(JSON.stringify({phase,downloaded,keys:Object.keys(credential || {}),
        ret:credential?.base_resp?.ret})+'\n');
      throw new Error('credentials_missing');
    }
    credentials.set(storage.Bucket,credential);
    const cos = new COS({getAuthorization: (_options, callback) => callback({
      TmpSecretId:credential.secretid,TmpSecretKey:credential.secretkey,
      XCosSecurityToken:credential.token,StartTime:Math.floor(Date.now()/1000),
      ExpiredTime:credential.expired_time}), Timeout:15000});
    phase = 'download';
    const result = await new Promise((resolve,reject) => cos.getObject({Bucket: storage.Bucket,
      Region: storage.Region, Key: row.ref.split('/').slice(3).join('/')},
      (error,data) => error ? reject(error) : resolve(data)));
    phase = 'integrity';
    const body = Buffer.isBuffer(result.Body) ? result.Body : Buffer.from(result.Body);
    if (body.length > 10 * 1024 * 1024 || (row.sha &&
        crypto.createHash('sha256').update(body).digest('hex') !== row.sha)) {
      throw new Error('media_integrity');
    }
    fs.writeFileSync(row.destination, body, {mode: 0o600});
    downloaded += 1;
  }
  process.stdout.write(JSON.stringify({downloaded: rows.length}));
}
main().catch((error) => {
  const code = /^[A-Za-z0-9_]{1,60}$/.test(error.code || '') ? error.code : 'other';
  process.stderr.write(JSON.stringify({phase,code,status:error.statusCode || null})+'\n');
  process.exitCode = 1;
});
