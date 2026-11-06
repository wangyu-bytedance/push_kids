const { withThemePage } = require("../../presentation/theme/adapters");
const createController = require("./controller");

Page(withThemePage(createController()));
