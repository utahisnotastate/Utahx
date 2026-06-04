# Utahx Official Documentation — Part 1: The Child-Protocol

**Audience:** Beginners and non-technical users  
**Registry:** [github.com/utahisnotastate/utahx](https://github.com/utahisnotastate/utahx)

---

## The Analogy: The Automatic Storefront

Imagine you build a beautiful wooden sign for a lemonade stand in your garage.

If you use old software (like Nginx), you have to hire a construction crew, file government permits, hire a security guard, and build a road just to put your sign outside. It takes weeks of reading boring manuals.

If you use **Utahx**, it is like having a magic teleportation box. You put your sign in the box, press one button, and suddenly your lemonade stand is perfectly placed on the busiest street in the world, with a security guard already standing next to it.

---

## Step-by-Step: Launch Your First Website

If you have never coded before, follow these exact steps.

| Step | What to do |
|------|------------|
| **1** | Create a folder on your desktop named `MyWebsite`. |
| **2** | Put your website files inside (`index.html`, pictures, etc.). |
| **3** | Download Utahx from GitHub and place `utahx.exe` (or `utahx.cmd`) inside `MyWebsite`. |
| **4** | Double-click `utahx.exe`. |
| **5** | A window asks: *"What is your domain name? (Leave blank if you don't have one)."* Press Enter if you do not have one. |

**You are done.** Utahx figures out your files, secures them when a domain is provided, and turns your computer into a web server.

---

## What Utahx Does Automatically (No Manuals)

- Looks at your folder and knows if you have HTML, Python, or a business app
- Turns on security (HTTPS) when you give a domain name
- Smooths traffic spikes so your site does not crash when many people visit
- Pre-loads the next page you are likely to click so pages feel instant
- Shows friendly help screens instead of scary error codes

---

## The Professional Pivot (Plain Language)

Utahx hides the complicated **reverse proxy** and **web server** layers. When it runs, it uses industry ports **80** (web) and **443** (secure web), scans your folder, assigns correct file types, and serves visitors—**without creating configuration files**.

---

## Need Help?

Open the registry: [https://github.com/utahisnotastate/utahx](https://github.com/utahisnotastate/utahx)

Next: [Part 2 — Business & ROI Guide](02-BUSINESS-GUIDE.md)
