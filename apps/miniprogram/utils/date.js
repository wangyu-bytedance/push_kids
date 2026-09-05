function pad(value) { return String(value).padStart(2, "0"); }

function localParts(value = new Date()) {
  return {
    date: `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())}`,
    time: `${pad(value.getHours())}:${pad(value.getMinutes())}`
  };
}

function toIso(date, time) {
  const value = new Date(`${date}T${time}:00`);
  return value.toISOString();
}

function friendlyTime(iso) {
  const value = new Date(iso);
  return `${value.getMonth() + 1}月${value.getDate()}日 ${pad(value.getHours())}:${pad(value.getMinutes())}`;
}

function monthKey(value = new Date()) { return localParts(value).date.slice(0, 7); }

module.exports = { localParts, toIso, friendlyTime, monthKey };
