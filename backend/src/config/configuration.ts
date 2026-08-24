export default () => ({
  port: parseInt(process.env.PORT || '3001', 10),
  database: {
    url: process.env.DATABASE_URL,
  },
  jwt: {
    secret: process.env.JWT_SECRET || 'super-secret-change-me',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  },
  genlayer: {
    rpcUrl: process.env.GENLAYER_RPC_URL || 'https://studio.genlayer.com/api',
    contractAddress: process.env.GENLAYER_CONTRACT_ADDRESS || '',
  },
  ipfs: {
    gateway: process.env.IPFS_GATEWAY || 'https://ipfs.io/ipfs/',
  },
});