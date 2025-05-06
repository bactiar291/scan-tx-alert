import requests
import json

with open("config.json", "r") as file:
    config = json.load(file)

API_KEY = config["api_key"]
ADDRESS = config["address"]
NETWORK = config["network"]

HIGH_RISK_ADDRESSES = {
    "0xb2a25f7d864636e44bc1bf7a316897652bf07463": "Known Drainer Contract (BSC)",
    "0xebbd18aa8130335fead576c78fc31dfd7f8b2dad": "PancakeSwap Fake Router (BSC)",
    "0x97a9a15168c22b3c137e6381037e1499c8ad0978": "Suspicious Deployer (ETH)"
}

def get_network_name():
    return "Binance Smart Chain" if NETWORK == "bsc" else "Ethereum"

def check_drain():
    api_url = "https://api.bscscan.com/api" if NETWORK == "bsc" else "https://api.etherscan.com/api"
    
    outgoing_tx = requests.get(
        f"{api_url}?module=account&action=txlist&address={ADDRESS}&startblock=0&endblock=99999999&sort=desc&apikey={API_KEY}"
    ).json()

    token_approvals = requests.get(
        f"{api_url}?module=account&action=tokentx&address={ADDRESS}&startblock=0&endblock=99999999&sort=desc&apikey={API_KEY}"
    ).json()

    internal_tx = requests.get(
        f"{api_url}?module=account&action=txlistinternal&address={ADDRESS}&startblock=0&endblock=99999999&sort=desc&apikey={API_KEY}"
    ).json()

    print(f"\n🔎 Analisis Alamat {ADDRESS} di Jaringan {get_network_name()}")
    print("══════════════════════════════════════")

    suspicious = False

    for tx in outgoing_tx["result"][:10]:
        if tx["to"] in HIGH_RISK_ADDRESSES:
            print(f"""
❗ [TRANSAKSI BERISIKO] ❗
• Tujuan: {tx['to']} 
• Keterangan: {HIGH_RISK_ADDRESSES.get(tx['to'], 'Scam Terdeteksi')}
• Hash TX: {tx['hash']}
• Tautan Explorer: {'https://bscscan.com/tx/'+tx['hash'] if NETWORK=='bsc' else 'https://etherscan.io/tx/'+tx['hash']}
            """)
            suspicious = True

    for approval in token_approvals["result"][:10]:
        contract = approval["contractAddress"]
        if contract in HIGH_RISK_ADDRESSES:
            print(f"""
⚠️ [APPROVAL BERBAHAYA] ⚠️  
• Kontrak: {contract}
• Token: {approval.get('tokenSymbol', 'Unknown')} ({approval.get('tokenName', 'Unknown')})
• Nilai Approval: {approval['value']} {approval.get('tokenSymbol', '')}
• Keterangan: {HIGH_RISK_ADDRESSES.get(contract, 'Kontrak Tidak Dikenal')}
• Tautan Explorer: {'https://bscscan.com/tx/'+approval['hash'] if NETWORK=='bsc' else 'https://etherscan.io/tx/'+approval['hash']}
            """)
            suspicious = True

    for tx in internal_tx["result"][:5]:
        if tx["from"] != ADDRESS.lower():
            print(f"""
🔍 [AKTIVITAS KONTRAK ASING] 🔍
• Pemanggil: {tx['from']}
• Nilai: {tx['value']} Wei
• Hash TX: {tx['hash']}
• Tautan Explorer: {'https://bscscan.com/tx/'+tx['hash'] if NETWORK=='bsc' else 'https://etherscan.io/tx/'+tx['hash']}
            """)
            suspicious = True

    if not suspicious:
        print("✅ Tidak ada aktivitas mencurigakan terdeteksi.")
    else:
        print("\n🚨🚨 **PERINGATAN KRITIS** 🚨🚨")
        print("""Alamat Anda memiliki interaksi dengan kontrak berisiko!
1. Segera REVOKE APPROVAL di: https://revoke.cash
2. Transfer semua aset ke dompet baru!
3. Laporkan alamat scam ke: https://chainabuse.com""")

if __name__ == "__main__":
    check_drain()
