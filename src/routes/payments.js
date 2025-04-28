const express = require('express');
const router = express.Router();
const { logger } = require('../utils/logger');
const { validatePayment } = require('../middleware/validation');
const { paymentLimiter, failedPaymentLimiter } = require('../middleware/rateLimit');
const stripeService = require('../services/stripeService');

// Apply rate limiting to all payment routes
router.use(paymentLimiter);

router.post('/', validatePayment, async (req, res, next) => {
  try {
    const { amount, currency, paymentMethod: methodType, cardDetails } = req.body;
    logger.info('Processing payment', { amount, currency, methodType });

    // Create a payment method first
    const stripePaymentMethod = await stripeService.stripe.paymentMethods.create({
      type: 'card',
      card: {
        number: cardDetails.cardNumber,
        exp_month: parseInt(cardDetails.expiryDate.split('/')[0]),
        exp_year: parseInt(cardDetails.expiryDate.split('/')[1]),
        cvc: cardDetails.cvv,
      },
    });

    // Create and confirm the payment intent
    const paymentIntent = await stripeService.createPaymentIntent(
      amount,
      currency,
      stripePaymentMethod.id,
    );

    logger.info('Payment processed successfully', { paymentIntentId: paymentIntent.id });

    res.status(201).json({
      success: true,
      data: {
        id: paymentIntent.id,
        status: paymentIntent.status,
        amount: paymentIntent.amount / 100, // Convert from cents
        currency: paymentIntent.currency,
      },
    });
  } catch (error) {
    logger.error('Payment processing failed', { error });
    // Apply stricter rate limiting for failed attempts
    failedPaymentLimiter(req, res, next);
    next(error);
  }
});

// Add endpoint to check payment status
router.get('/:paymentIntentId', async (req, res, next) => {
  try {
    const { paymentIntentId } = req.params;
    const paymentIntent = await stripeService.retrievePaymentIntent(paymentIntentId);

    res.status(200).json({
      success: true,
      data: {
        id: paymentIntent.id,
        status: paymentIntent.status,
        amount: paymentIntent.amount / 100,
        currency: paymentIntent.currency,
      },
    });
  } catch (error) {
    logger.error('Failed to retrieve payment status', { error });
    next(error);
  }
});

module.exports = router;
