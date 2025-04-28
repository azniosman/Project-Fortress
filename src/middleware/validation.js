const { logger } = require('../utils/logger');

// Credit card validation utilities
const validateCreditCard = (cardNumber) => {
  // Remove any spaces or dashes
  const cleanNumber = cardNumber.replace(/[\s-]/g, '');
  
  // Check if it's a valid number (Luhn algorithm)
  let sum = 0;
  let isEven = false;
  
  for (let i = cleanNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cleanNumber.charAt(i), 10);
    
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
    isEven = !isEven;
  }
  
  return sum % 10 === 0;
};

const validateExpiryDate = (expiryDate) => {
  const [month, year] = expiryDate.split('/');
  const currentDate = new Date();
  const currentYear = currentDate.getFullYear() % 100;
  const currentMonth = currentDate.getMonth() + 1;
  
  const expiryYear = parseInt(year, 10);
  const expiryMonth = parseInt(month, 10);
  
  if (expiryYear < currentYear || 
      (expiryYear === currentYear && expiryMonth < currentMonth)) {
    return false;
  }
  
  return true;
};

const validateCVV = (cvv) => {
  return /^\d{3,4}$/.test(cvv);
};

const validatePayment = (req, res, next) => {
  const { amount, currency, paymentMethod, cardDetails } = req.body;

  // Validate required fields
  if (!amount || !currency || !paymentMethod) {
    logger.warn('Missing required payment fields', { body: req.body });
    return res.status(400).json({
      success: false,
      error: 'Missing required fields: amount, currency, and paymentMethod are required'
    });
  }

  // Validate amount
  if (typeof amount !== 'number' || amount <= 0) {
    logger.warn('Invalid amount', { amount });
    return res.status(400).json({
      success: false,
      error: 'Amount must be a positive number'
    });
  }

  // Validate currency
  const validCurrencies = ['USD', 'EUR', 'GBP'];
  if (!validCurrencies.includes(currency)) {
    logger.warn('Invalid currency', { currency });
    return res.status(400).json({
      success: false,
      error: `Currency must be one of: ${validCurrencies.join(', ')}`
    });
  }

  // Validate payment method
  const validPaymentMethods = ['credit_card', 'bank_transfer'];
  if (!validPaymentMethods.includes(paymentMethod)) {
    logger.warn('Invalid payment method', { paymentMethod });
    return res.status(400).json({
      success: false,
      error: `Payment method must be one of: ${validPaymentMethods.join(', ')}`
    });
  }

  // Validate credit card details if payment method is credit_card
  if (paymentMethod === 'credit_card') {
    if (!cardDetails) {
      logger.warn('Missing card details for credit card payment');
      return res.status(400).json({
        success: false,
        error: 'Card details are required for credit card payments'
      });
    }

    const { cardNumber, expiryDate, cvv } = cardDetails;

    if (!cardNumber || !expiryDate || !cvv) {
      logger.warn('Missing required card details', { cardDetails });
      return res.status(400).json({
        success: false,
        error: 'Card number, expiry date, and CVV are required'
      });
    }

    if (!validateCreditCard(cardNumber)) {
      logger.warn('Invalid card number', { cardNumber });
      return res.status(400).json({
        success: false,
        error: 'Invalid card number'
      });
    }

    if (!validateExpiryDate(expiryDate)) {
      logger.warn('Invalid expiry date', { expiryDate });
      return res.status(400).json({
        success: false,
        error: 'Card has expired or invalid expiry date'
      });
    }

    if (!validateCVV(cvv)) {
      logger.warn('Invalid CVV', { cvv });
      return res.status(400).json({
        success: false,
        error: 'Invalid CVV'
      });
    }
  }

  next();
};

module.exports = {
  validatePayment
}; 