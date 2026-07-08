# Tesla Mail — Internal (Mockup)

A quick, self-contained UI mockup of a Tesla internal email client.

- Single static file: `index.html` (no build step, no dependencies).
- Sample account: `chongzhe@tesla.com`
- Includes mock emails, folders, labels, and a reading pane.

> This is a design mockup for demonstration only. It is **not affiliated with,
> endorsed by, or connected to Tesla, Inc.** The Tesla name and logo are
> trademarks of their respective owner and are used here purely to illustrate a
> UI concept.

## Deploy to Vercel

This is a zero-config static site. From this directory:

```bash
vercel deploy --prod --yes
```

You must be authenticated first (`vercel login`, or set `VERCEL_TOKEN` and pass
`--token "$VERCEL_TOKEN"`).
