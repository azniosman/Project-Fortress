const Stripe = require('stripe');
const { logger } = require('../utils/logger');

class StripeService {
  constructor() {
    this.stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  }

  async createPaymentIntent(amount, currency, paymentMethod) {
    try {
      const paymentIntent = await this.stripe.paymentIntents.create({
        amount: Math.round(amount * 100), // Convert to cents
        currency: currency.toLowerCase(),
        payment_method: paymentMethod,
        confirm: true,
        automatic_payment_methods: {
          enabled: true,
          allow_redirects: 'never',
        },
      });

      logger.info('Payment intent created', { paymentIntentId: paymentIntent.id });
      return paymentIntent;
    } catch (error) {
      logger.error('Failed to create payment intent', { error });
      throw error;
    }
  }

  async retrievePaymentIntent(paymentIntentId) {
    try {
      const paymentIntent = await this.stripe.paymentIntents.retrieve(paymentIntentId);
      logger.info('Payment intent retrieved', { paymentIntentId });
      return paymentIntent;
    } catch (error) {
      logger.error('Failed to retrieve payment intent', { error });
      throw error;
    }
  }
}

module.exports = new StripeService();
