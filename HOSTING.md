# Hosting everyitem.app (researched October 21, 2026)

Nothing has been deployed and no accounts have been created. This page is the plan.

**Current DNS (checked Oct 21, 2026 via public DNS):** everyitem.app uses Porkbun's nameservers (`*.ns.porkbun.com`). It still has Porkbun's default parking records: the apex and a `*` wildcard both point to `pixie.porkbun.com` (207.207.210.107 / .229). There are no MX or CAA records.

## Comparison

| | Porkbun Static Hosting | **GitHub Pages** (top pick) | Cloudflare Pages | Netlify |
| --- | --- | --- | --- | --- |
| Cost | **Not free:** 15-day free trial, then $3-$6/month or $30-$60/year [1][2] | Free (on GitHub Free the repository must be **public**) [7] | Free [10] | Free plan: 300 credits/month, hard cap, and sites **pause** when you run out [13] |
| How you upload | File editor, FTP, or GitHub Connect (pushes to a repo auto-update the site) [3][4] | Git push. The included workflow builds with Python and publishes. | Drag and drop the `dist/` folder or a zip in the dashboard, or Git [11] | Drag and drop, Git or CLI |
| DNS stays at Porkbun? | Yes | **Yes.** Porkbun has a one-click "GitHub" Quick DNS Config [5] | **No** for the apex domain: you must move the nameservers to Cloudflare (external DNS only works for subdomains) [8][9] | Yes (A record `75.2.60.5` + www CNAME) [14] |
| HTTPS | Free SSL [1] | Free automatic certificate plus an "Enforce HTTPS" option [6] | Automatic | Automatic [15] |
| Limits | 2-5 GB disk, 40 MB upload limit [1][4] | 1 GB site, soft 100 GB/month bandwidth [7] | 20,000 files, 25 MiB per file, 500 builds/month [10] | Credit-based |
| Notes | Simplest dashboard, but it costs money | Most beginner-friendly free option that keeps DNS where it is | Cloudflare now says "Start new projects with Workers" on its Pages docs, though Pages still works [12] | The credit cap is a risk if a guide goes viral |

### Recommendation: GitHub Pages

- It's **free**, and your **DNS stays at Porkbun**, which has a built-in "GitHub" DNS button [5].
- It **builds automatically**. `.github/workflows/deploy.yml` is already in this project, so after setup you edit a Markdown file (even in GitHub's website editor), commit, and the site updates.
- HTTPS is automatic, which `.app` requires (see below).
- Trade-off: on a free GitHub account the repository has to be public, so people can see the site's source. That's fine for a marketing site because it contains no secrets.

**Runner-up:** Cloudflare Pages with drag-and-drop upload, if you'd rather never touch Git. It's free with generous limits, but you must move everyitem.app's nameservers from Porkbun to Cloudflare (and turn off DNSSEC at Porkbun first if it's on) [8][9], and you re-upload `dist/` by hand after each build.

**Skip:** Porkbun Static Hosting (paid after the trial), and Netlify (the free plan pauses sites at the credit cap).

## About `.app` and HTTPS

`.app` is on browsers' **HSTS preload list for the whole TLD**. Browsers will only load everyitem.app over HTTPS; plain `http://` is upgraded automatically, and the site **fails to load** if there's no valid certificate [16][17]. In practice:
- After you point DNS at GitHub, the site will show a certificate error until GitHub issues the certificate. That can take up to an hour, and "Enforce HTTPS" can take up to 24 hours to become available [6][18]. This is expected, so just wait.
- You don't need to submit anything to hstspreload.org. The TLD is already preloaded.
- Every subdomain you ever use (www, etc.) also needs HTTPS.

## Step-by-step: GitHub Pages + Porkbun DNS

Replace `USERNAME` with your GitHub username.

**A. Put the site on GitHub**
1. Create a free GitHub account if you don't have one, then create a **new public repository**, e.g. `everyitem-site`. Don't add a README; this project already has one.
2. Upload this folder. The easiest way is GitHub Desktop: *File > Add local repository*, then pick the `everyitem-site` folder, *Publish repository*, and untick "Keep this code private". Or from Terminal:
   ```bash
   cd everyitem-site
   git init && git add . && git commit -m "First version of everyitem.app"
   git branch -M main
   git remote add origin https://github.com/USERNAME/everyitem-site.git
   git push -u origin main
   ```
   (`dist/` and `preview/` are in `.gitignore`. GitHub builds the site itself.)
3. In the repo, go to **Settings > Pages > Build and deployment > Source** and choose **GitHub Actions**. The included workflow runs, builds the site, runs the link checker, and publishes it to `https://USERNAME.github.io/everyitem-site/`. Check the **Actions** tab for a green tick. CSS may look broken at that temporary address because the site uses root links; it works on everyitem.app.

**B. Verify the domain (prevents takeover)** [19]
4. Go to GitHub **profile** Settings (not the repo) > **Pages** > **Add a domain**, enter `everyitem.app`, and GitHub shows a TXT record.
5. In Porkbun, open Domain Management, click **DNS** next to everyitem.app, and add:

   | Type | Host | Answer |
   | --- | --- | --- |
   | TXT | `_github-pages-challenge-USERNAME` | *(the code GitHub shows)* |

   Then click **Verify** on GitHub. Keep this record forever.

**C. Point DNS to GitHub** [5][6][18]
6. In Porkbun DNS, **delete the default parking records**: the `ALIAS` record for everyitem.app pointing to `pixie.porkbun.com` and the **wildcard `*` CNAME** pointing to `pixie.porkbun.com`. GitHub warns that wildcard records risk domain takeover [19].
7. Add these records. Porkbun's **Quick DNS Config > "GitHub"** button creates the A records for you [5]. Check the result matches:

   | Type | Host | Answer |
   | --- | --- | --- |
   | A | *(blank)* | `185.199.108.153` |
   | A | *(blank)* | `185.199.109.153` |
   | A | *(blank)* | `185.199.110.153` |
   | A | *(blank)* | `185.199.111.153` |
   | AAAA | *(blank)* | `2606:50c0:8000::153` |
   | AAAA | *(blank)* | `2606:50c0:8001::153` |
   | AAAA | *(blank)* | `2606:50c0:8002::153` |
   | AAAA | *(blank)* | `2606:50c0:8003::153` |
   | CNAME | `www` | `USERNAME.github.io` |

   Don't add any other A, AAAA or ALIAS records on the blank host, because extras block the certificate [6]. If you ever add CAA records, include `letsencrypt.org` [18].
8. In the repo, go to **Settings > Pages > Custom domain**, enter `everyitem.app` and click **Save**. With the Actions workflow, no `CNAME` file is needed [18]. GitHub redirects `www.everyitem.app` to `everyitem.app` automatically.
9. Wait for the DNS check to pass and the certificate to be issued (minutes, sometimes up to 24 hours). Then tick **Enforce HTTPS**.
10. Visit `https://everyitem.app` and `https://www.everyitem.app`. If HTTPS stays unavailable after an hour, remove and re-add the custom domain to retrigger it [18].

**D. After it's live**
11. Add the site to Google Search Console (a DNS TXT record at Porkbun) and submit `https://everyitem.app/sitemap.xml`.
12. Support email: Porkbun's free email forwarding (Domain Management > Email > create `support@` forwarding to your personal inbox). Make sure the MX records `fwd1.porkbun.com` (priority 10) and `fwd2.porkbun.com` (priority 20) and the TXT record `v=spf1 include:_spf.porkbun.com ~all` exist on the apex, and add them if Porkbun didn't [20][21]. Then set `support_email_ready` to `True` in `build.py`.

From then on, publishing is: edit or add a Markdown file, commit, push (or edit on github.com), and the site updates in about a minute.

## Sources

1. Porkbun Static Hosting product page: https://porkbun.com/products/webhosting/staticHosting
2. Porkbun Web Hosting comparison (Static Hosting $3-$6/mo, $30-$60/yr): https://porkbun.com/products/web_hosting
3. Porkbun KB, How to connect Static Hosting to GitHub: https://kb.porkbun.com/article/145-how-to-connect-static-hosting-to-github
4. Porkbun KB, How to set up Static Hosting (40 MB upload limit): https://kb.porkbun.com/article/137-how-to-set-up-static-hosting
5. Porkbun KB, How to connect your domain to GitHub Pages (Quick DNS Config): https://kb.porkbun.com/article/64-how-to-connect-your-domain-to-github-pages
6. GitHub Docs, Securing your GitHub Pages site with HTTPS: https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https
7. GitHub Docs, GitHub Pages limits, and GitHub's plans (Pages on public repos for GitHub Free): https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits and https://docs.github.com/en/get-started/learning-about-github/githubs-plans
8. Cloudflare Docs, Pages custom domains (apex requires a Cloudflare zone/nameservers): https://developers.cloudflare.com/pages/configuration/custom-domains/
9. Cloudflare Docs, Change your nameservers (turn off DNSSEC first): https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/
10. Cloudflare Docs, Pages limits: https://developers.cloudflare.com/pages/platform/limits/
11. Cloudflare Docs, Pages Direct Upload (drag and drop): https://developers.cloudflare.com/pages/get-started/direct-upload/
12. Cloudflare Docs, Pages getting started ("Start new projects with Workers"): https://developers.cloudflare.com/pages/get-started/
13. Netlify Docs, Credit-based pricing plans: https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/
14. Netlify Docs, Configure external DNS: https://docs.netlify.com/manage/domains/configure-domains/configure-external-dns/
15. Netlify Docs, HTTPS (SSL): https://docs.netlify.com/manage/domains/secure-domains-with-https/https-ssl
16. Google Registry, .app: https://get.app/
17. Porkbun KB, HSTS Preload and Google Registry: https://kb.porkbun.com/article/96-hsts-preload-and-google-registry
18. GitHub Docs, Managing a custom domain / Troubleshooting custom domains: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site and https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages
19. GitHub Docs, Verifying your custom domain for GitHub Pages: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages
20. Porkbun KB, How to set up email forwarding: https://kb.porkbun.com/article/10-how-to-set-up-email-forwarding-service
21. Porkbun KB, Using Porkbun email when DNS is elsewhere (MX/SPF values): https://kb.porkbun.com/article/47-how-to-use-porkbun-email-when-your-dns-is-hosted-elsewhere
