const { withThemePage } = require("../../presentation/theme/adapters");
const controller = require("./controller");

Page(withThemePage(controller));
