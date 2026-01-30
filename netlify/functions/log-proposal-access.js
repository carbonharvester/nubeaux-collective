// Netlify function to log proposal access
// View logs in Netlify dashboard: Functions > log-proposal-access > Logs

exports.handler = async (event, context) => {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const data = JSON.parse(event.body);
    const { name, email, proposal, timestamp, userAgent } = data;

    // Log to Netlify function logs (viewable in dashboard)
    console.log('=== PROPOSAL ACCESS ===');
    console.log(`Proposal: ${proposal}`);
    console.log(`Name: ${name}`);
    console.log(`Email: ${email}`);
    console.log(`Time: ${timestamp}`);
    console.log(`User Agent: ${userAgent}`);
    console.log(`IP: ${event.headers['x-forwarded-for'] || event.headers['client-ip'] || 'unknown'}`);
    console.log('========================');

    // Optional: Send to webhook (Slack, Discord, email service, etc.)
    // Uncomment and configure WEBHOOK_URL in Netlify environment variables
    /*
    if (process.env.WEBHOOK_URL) {
      await fetch(process.env.WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `Proposal accessed: ${proposal}\nName: ${name}\nEmail: ${email}\nTime: ${timestamp}`
        })
      });
    }
    */

    // Optional: Send email via SendGrid, Mailgun, etc.
    // Configure API keys in Netlify environment variables

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      body: JSON.stringify({ success: true, message: 'Access logged' })
    };

  } catch (error) {
    console.error('Error logging access:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to log access' })
    };
  }
};
