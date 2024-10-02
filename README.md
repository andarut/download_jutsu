# ⚙️ download_jutsu

Script to download any anime from https://jut.su/

# Demo

You need python3.11 installed on your system.
Also install dev chrome automated driver [version 131](https://googlechromelabs.github.io/chrome-for-testing/#dev) and replace `driver` with it.
If you are on macOS executable will be in `.app/Content/MacOS/`
Also if you are from Russia - turn off VPN, Cloudflare don't like it.

```bash
./demo.sh
```

**give it time, because timeouts are placed for old hardware**

it will download first 3 episods of One Piece. You delete like below `# DEMO` and it will be downloading all episods

## TODO:
- save progress urls in txt

## Message for jutsu

**Your website is great and i want to give people possibility to download anime and watch it offline.**

Throught my code you will see how i managed to download from your website. **To be short and polity i explain "hack" steps by steps:**

1. Check main page (get title and episodes count)
2. Episods downloaded with curl using hash from last session
3. Cloudflare sucks if i use undetected selenium driver

If you modify you storage system i will continue to modifing this script, because i want to watch anime offline without your ads. Anyway i think you don't give a fuck about this script, so i just wanna tell you that i am not using it in wrong way, just for myself.
