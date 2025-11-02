# Deployment Guide

## Automatic Deployment (GitHub Actions)

The site is configured to automatically deploy to GitHub Pages when you push to the `main` branch.

### Setup Steps:

1. **Enable GitHub Pages in your repository settings:**
   - Go to your repository on GitHub
   - Click on **Settings** → **Pages**
   - Under "Build and deployment":
     - Source: Select **GitHub Actions**
   - Save the settings

2. **Push your code:**
   ```bash
   git add .
   git commit -m "Setup GitHub Pages deployment"
   git push origin main
   ```

3. **Wait for deployment:**
   - Go to the **Actions** tab in your GitHub repository
   - You'll see the workflow running
   - Once complete, your site will be live at: `https://dmitriik.github.io/Turkish-language/`

4. **Access your site:**
   - After deployment completes, visit: **https://dmitriik.github.io/Turkish-language/**

## Manual Deployment (Alternative)

If you prefer to deploy manually using gh-pages:

```bash
cd frontend
npm run deploy
```

This will build and deploy to the `gh-pages` branch.

## Troubleshooting

- **404 errors for assets**: Make sure the `base` path in `vite.config.ts` matches your repository name
- **Workflow not running**: Check that GitHub Actions is enabled in your repository settings
- **Build failures**: Check the Actions tab for error logs

## Local Development

```bash
cd frontend
npm install
npm run dev
```

This will start the development server at `http://localhost:3000`
