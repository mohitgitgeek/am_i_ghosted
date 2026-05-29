# am_i_ghosted
My second project that focuses on Ghost Hiring.

## GitHub Pages Deployment

This repository now includes a GitHub Actions workflow at:

- `.github/workflows/deploy-pages.yml`

How to enable the deployment in GitHub:

1. Open repository **Settings** → **Pages**.
2. Under **Build and deployment**, choose **Source: GitHub Actions**.
3. Push to `main` (or run the workflow manually from the Actions tab).
4. GitHub Pages will publish the static site from the workflow artifact.

### Notes

- `index.html` redirects to `check_ghosting.html`.
- Application entries are stored in browser `localStorage`.
- `applications.html` reads/deletes entries from `localStorage`.

SCREENSHOTS :

Main Menu :
![{1C2CF6A9-332B-4C1C-AD17-89574CBEDFA7}](https://github.com/user-attachments/assets/1d490d40-49dc-4391-ab4b-9ff115ca459f)

This is the history of applications :
![{B9017136-AC06-4A12-9C6B-7E23A2E1AE7C}](https://github.com/user-attachments/assets/acee3d24-42b6-4856-9838-1a8c14e78df7)
