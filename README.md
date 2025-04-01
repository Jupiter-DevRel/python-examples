# Jupiter Exchange API Python Code Examples

This repo contains practical code examples and implementations designed to help developers work with the [Jupiter Exchange APIs](https://station.jup.ag/docs/). Our goal is to empower developers with the knowledge and inspiration to build innovative applications leveraging Jupiter's ecosystem.

---

## Getting Started

1. Clone this repository:
```bash
git clone https://github.com/Jupiter-DevRel/python-examples.git
cd python-examples
```

2. Set up the required environment variables:

   - Scripts in this repository rely on environment variables to securely store sensitive information such as private keys, RPC URLs, and optional API keys for Jupiter's API.

   - Copy the file `.env-example` to `.env`:

     ```bash
     cp .env-example .env
     ```

   - Open the `.env` file and fill in the required values:

     ```bash
     PRIVATE_KEY=your_private_key_here
     RPC_URL=https://your_rpc_url_here
     API_KEY=your_jupiter_api_key_here
     ```

      - `PRIVATE_KEY`: This is your Base58-encoded private key used to sign transactions.
      - `RPC_URL`: This is the URL for your Solana RPC provider.
      - `API_KEY` *(optional)*: Your Jupiter API key if you’ve purchased a plan. Jupiter APIs can be used without an API key for free, but if you want a paid plan with access to higher limits, you can obtain an API key at [Jupiter API Portal](http://portal.jup.ag/).

     **Note:**
      - Using a Solana native RPC provider with **staked connections** is highly recommended to ensure your transactions will be landing. If you're unsure what this is, read more here: [stake-weighted QoS (Quality of Service)](https://solana.com/developers/guides/advanced/stake-weighted-qos).
      - If you do not have access to a staked RPC provider, you can use Solana's default mainnet endpoint:  
        `https://api.mainnet-beta.solana.com`.

3. Navigate to the code example you want to run, for example:
```bash
cd swap-api/simple-quote-and-swap/
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

5. Run any example script in the repository:
```bash
python main.py
```

Each example in this repository has its own `requirements.txt` file to list the specific dependencies needed to run that script.

6. Review the documentation to explore the full potential of the Jupiter Exchange APIs and learn how to integrate them into your projects:
   - [Jupiter API Docs](https://station.jup.ag/docs/)
   - [API Guides](https://station.jup.ag/guides/)

---

## Getting Help

If you have any questions or run into issues, feel free to reach out to us in the **#developer-support** channel on our Discord server:  
👉 [Join Jupiter Discord](https://discord.gg/jup)

---

## Contribution Guidelines

We welcome contributions to this repository! To contribute:
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your work (`git commit -m "Add feature-name"`).
4. Push to the branch (`git push origin feature-name`).
5. Submit a pull request for review.

---

## Powered by the Jupiter DevRel Working Group

This repository and its content are developed and maintained by the **Jupiter DevRel Working Group** to support and inspire the developer community. We aim to showcase the full potential of Jupiter APIs, and we’re always excited to see what you build!

**Happy coding! 🚀**