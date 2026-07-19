const { getHealthStatus } = require("../services/health.service");

const healthCheck = (req, res) => {

    const response = getHealthStatus();

    res.status(200).json(response);

};

module.exports = {
    healthCheck,
};