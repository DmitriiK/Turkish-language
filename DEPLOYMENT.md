# Deployment Guide

## Automatic Deployment (GitHub Actions)

The site is configured to automatically deploy to GitHub Pages when you push to the `main` branch.

### Setup Steps:

1. **First, commit and push the workflow file:**
   ```bash
   git add .github/workflows/deploy.yml
   git add frontend/public/.nojekyll
   git commit -m "Add GitHub Pages deployment workflow"
   git push origin main
   ```

2. **Enable GitHub Pages in your repository settings:**
   - Go to: https://github.com/DmitriiK/Turkish-language/settings/pages
   - Under "Build and deployment":
     - **Source**: Select **GitHub Actions** (NOT "Deploy from a branch")
   - Save the settings

3. **Trigger the deployment:**
   - The workflow will run automatically on the next push, OR
   - Go to: https://github.com/DmitriiK/Turkish-language/actions
   - Click on "Deploy to GitHub Pages" workflow
   - Click "Run workflow" button to manually trigger it

4. **Wait for deployment:**
   - Go to the **Actions** tab in your GitHub repository
   - You'll see the workflow running
   - Once complete (should take 2-3 minutes), your site will be live

5. **Access your site:**
   - After deployment completes, visit: **https://dmitriik.github.io/Turkish-language/**

## Important Notes

- The site has ~11,850 files (all the training data), so deployment may take a few minutes
- Make sure the "Source" in GitHub Pages settings is set to **GitHub Actions**, not "gh-pages branch"
- If you see only the README, the Pages source is likely set incorrectly

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
