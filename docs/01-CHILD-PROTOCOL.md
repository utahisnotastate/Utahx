# Part 1: The Child-Protocol

**Audience:** Beginners and non-technical users  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## The analogy: the automatic storefront

Imagine you build a wooden sign for a lemonade stand in your garage.

**Old way (Nginx and similar tools):** You hire a crew, file permits, hire a guard, and build a road before anyone can see your sign. One typo in a configuration file can lock the door. That takes days or weeks of manuals.

**Utahx way:** You place your sign in a magic box, press one button, and your stand appears on a busy street with security already in place.

Utahx is that box for websites.

---

## What you need before you start

- A computer (Windows, Mac, or Linux)
- A folder with your site files (at minimum an `index.html` page)
- Optional: a domain name you own (for example `myshop.com`)

You do **not** need to understand programming, Nginx, or SSL certificates.

---

## Step-by-step: launch your first website

| Step | Action |
|------|--------|
| 1 | Create a folder on your desktop named `MyWebsite`. |
| 2 | Copy your site files into it (`index.html`, images, etc.). |
| 3 | Download Utahx from [GitHub](https://github.com/utahisnotastate/Utahx) and place `utahx.cmd` or `utahx.exe` inside `MyWebsite`. |
| 4 | Double-click the Utahx file. |
| 5 | When asked for a domain name, type yours or press **Enter** to skip (local testing only). |

**Done.** Utahx reads your folder, chooses how to serve it, and starts a web server. If you entered a domain, it also works on securing the connection (HTTPS).

Your site is usually available at `http://localhost:8080` when no domain is set.

---

## What Utahx does without you configuring anything

| Feature | What it means for you |
|---------|------------------------|
| **Auto-sensing** | Detects HTML, Python, or Node.js projects from files in the folder |
| **Auto-security** | Requests and installs TLS certificates when you provide a domain |
| **Traffic smoothing** | Slows requests slightly during spikes instead of showing scary errors |
| **Pre-fetching** | Guesses the next page you might open and loads it early |
| **Friendly errors** | Shows clear help screens instead of `502 Bad Gateway` |

---

## Common questions

**Do I need to write a configuration file?**  
No. Utahx deliberately avoids files like `nginx.conf`.

**Will my site work on the real internet?**  
With a domain and proper DNS pointing to your machine or cloud server, yes. For home networks you may need your ISP or router to allow inbound traffic on ports 80 and 443.

**What if something breaks?**  
Utahx shows a plain-English screen explaining the problem. Developers get extra hints in the same view.

---

## The professional pivot (plain language)

Behind the scenes, Utahx acts as a **reverse proxy** and **web server**. It listens on standard ports **80** (web) and **443** (secure web), inspects your project folder, and routes visitors to the right content. Operators get enterprise behavior without editing config files.

---

## Troubleshooting quick tips

| Issue | What to try |
|-------|-------------|
| Blank page locally | Open `http://localhost:8080`; confirm `index.html` exists |
| Domain not working | Point DNS A/AAAA record to your server; check firewall |
| Window closes instantly on Windows | Run from terminal: `py -3.11 utahx_launcher.py` to read errors |

---

## Safety reminder

Utahx exposes your computer or server to the network when you bind to public ports. Use a domain and TLS for production, keep your operating system updated, and do not expose admin tools on the same port without authentication.

---

## Where to go next

- Business impact: [Part 2 — Business Guide](02-BUSINESS-GUIDE.md)  
- Technical setup: [Part 3 — Migration Guide](03-MIGRATION-GUIDE.md)  
- Full doc index: [docs/README.md](README.md)
