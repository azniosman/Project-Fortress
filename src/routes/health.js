const express = require('express');
const router = express.Router();
const { logger } = require('../utils/logger');

router.get('/', (req, res) => {
  const healthcheck = {
    uptime: process.uptime(),
    message: 'OK',
    timestamp: Date.now(),
    environment: process.env.NODE_ENV || 'development'
  };

  logger.info('Health check performed', { healthcheck });
  res.status(200).json(healthcheck);
});

module.exports = router; 