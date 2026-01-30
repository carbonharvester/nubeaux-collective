// Netlify Edge Function - Image Hotlink Protection
export default async (request, context) => {
  const url = new URL(request.url);
  const pathname = url.pathname.toLowerCase();

  // Check if request is for an image
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'];
  const isImage = imageExtensions.some(ext => pathname.endsWith(ext));

  if (!isImage) {
    return context.next();
  }

  // Get the referer header
  const referer = request.headers.get('referer');

  // Allowed domains (add your domain here)
  const allowedDomains = [
    'nubeauxcollective.com',
    'www.nubeauxcollective.com',
    'nubeaux-collective.netlify.app',
    'localhost',
    '127.0.0.1',
    // Cloudinary is allowed (our CDN)
    'res.cloudinary.com'
  ];

  // If no referer, could be direct access - allow for now but you can block
  if (!referer) {
    return context.next();
  }

  // Check if referer is from allowed domain
  try {
    const refererUrl = new URL(referer);
    const refererHost = refererUrl.hostname.toLowerCase();

    const isAllowed = allowedDomains.some(domain =>
      refererHost === domain || refererHost.endsWith('.' + domain)
    );

    if (!isAllowed) {
      // Return 403 Forbidden for hotlinked images
      return new Response('Hotlinking not allowed', {
        status: 403,
        headers: {
          'Content-Type': 'text/plain',
        }
      });
    }
  } catch (e) {
    // Invalid referer URL, allow request
  }

  return context.next();
};

export const config = {
  path: ["/assets/*", "/*.jpg", "/*.jpeg", "/*.png", "/*.webp"]
};
