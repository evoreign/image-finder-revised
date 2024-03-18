/** @type {import('next').NextConfig} */
const nextConfig = {
images: {
    remotePatterns: [
        {
            protocol: 'https',
            hostname: 'res.cloudinary.com',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'bing.com',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'i.pinimg.com',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'th.bing.com',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 's7d2.scene7.com',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'd.gongchengbing.com',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'komatsu.stylelabs.cloud',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'www.komatsu.eu',
            pathname: '**',
        },
        {
            protocol: 'https',
            hostname: 'www.liebherr.com',
            pathname: '**',
        },
    ],
    },
};

export default nextConfig;