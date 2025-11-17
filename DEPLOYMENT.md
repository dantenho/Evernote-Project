# Production Deployment Guide

This guide provides comprehensive instructions for deploying the LearnHub application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Setup](#database-setup)
6. [Post-Deployment](#post-deployment)
7. [Deployment Platforms](#deployment-platforms)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm/yarn installed
- **PostgreSQL 14+** database
- **Git** for version control
- Account on chosen hosting platform (Heroku, DigitalOcean, AWS, etc.)

---

## Environment Configuration

### Backend Environment Variables

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Configure the following environment variables in `.env`:

   ```bash
   # Django Core Settings
   DJANGO_SECRET_KEY=your-super-secret-key-here-change-this-in-production
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

   # Database Configuration
   DB_NAME=webapp
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password_here
   DB_HOST=your-database-host.com
   DB_PORT=5432

   # CORS Configuration
   CORS_ALLOWED_ORIGINS=https://your-frontend.netlify.app,https://www.your-domain.com

   # Security Settings
   SECURE_SSL_REDIRECT=True
   ```

3. **Generate a secure SECRET_KEY**:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

### Frontend Environment Variables

1. Copy the frontend environment template:
   ```bash
   cd frontend
   cp .env.example .env.production
   ```

2. Configure the API URL:
   ```bash
   VITE_API_BASE_URL=https://your-backend-api.herokuapp.com/api/v1
   VITE_APP_ENV=production
   ```

---

## Backend Deployment

### Option 1: Heroku Deployment

1. **Install Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Set environment variables**:
   ```bash
   heroku config:set DJANGO_SECRET_KEY=your-secret-key
   heroku config:set DJANGO_DEBUG=False
   heroku config:set DJANGO_ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```

6. **Deploy to Heroku**:
   ```bash
   git push heroku main
   ```

7. **Run migrations**:
   ```bash
   heroku run python manage.py migrate
   ```

8. **Create a superuser**:
   ```bash
   heroku run python manage.py createsuperuser
   ```

### Option 2: DigitalOcean App Platform

1. **Connect your GitHub repository** via the DigitalOcean dashboard

2. **Configure build settings**:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Run Command**: `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`

3. **Add PostgreSQL database** from the DigitalOcean marketplace

4. **Set environment variables** in the App Platform dashboard

5. **Deploy** and wait for the build to complete

### Option 3: AWS Elastic Beanstalk

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**:
   ```bash
   eb init -p python-3.11 your-app-name
   ```

3. **Create environment**:
   ```bash
   eb create production-env
   ```

4. **Set environment variables**:
   ```bash
   eb setenv DJANGO_SECRET_KEY=your-secret-key DJANGO_DEBUG=False
   ```

5. **Deploy**:
   ```bash
   eb deploy
   ```

---

## Frontend Deployment

### Option 1: Netlify Deployment

1. **Build the frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Install Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   ```

3. **Login to Netlify**:
   ```bash
   netlify login
   ```

4. **Deploy**:
   ```bash
   netlify deploy --prod --dir=dist
   ```

5. **Configure environment variables** in Netlify dashboard:
   - `VITE_API_BASE_URL=https://your-backend.herokuapp.com/api/v1`

### Option 2: Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Set environment variables**:
   ```bash
   vercel env add VITE_API_BASE_URL production
   ```

### Option 3: AWS S3 + CloudFront

1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Create S3 bucket** for static hosting

3. **Upload dist/ folder** to S3:
   ```bash
   aws s3 sync dist/ s3://your-bucket-name --delete
   ```

4. **Configure CloudFront** distribution for the S3 bucket

5. **Set up custom domain** (optional)

---

## Database Setup

### PostgreSQL Production Database

1. **Create production database**:
   ```sql
   CREATE DATABASE webapp;
   CREATE USER your_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE webapp TO your_user;
   ```

2. **Update connection settings** in environment variables

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create initial achievements** (optional):
   ```bash
   python manage.py shell
   ```
   ```python
   from learning.models import Achievement

   Achievement.objects.create(
       name="First Step",
       description="Complete your first learning step",
       achievement_type="first_step",
       icon="🎯",
       xp_reward=50,
       order=1
   )
   # Add more achievements as needed
   ```

---

## Post-Deployment

### 1. Create Superuser

```bash
python manage.py createsuperuser
```

### 2. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 3. Verify Deployment

- Test backend API: `https://your-backend.com/api/v1/areas/`
- Test frontend: `https://your-frontend.com`
- Login to admin: `https://your-backend.com/admin/`

### 4. Set Up Monitoring

- Configure error tracking (e.g., Sentry)
- Set up uptime monitoring (e.g., UptimeRobot, Pingdom)
- Enable application logs

### 5. Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` generated
- ✅ HTTPS enabled (SSL certificate)
- ✅ `ALLOWED_HOSTS` configured correctly
- ✅ `CORS_ALLOWED_ORIGINS` set to frontend domain
- ✅ Database password is strong and secure
- ✅ All sensitive credentials in environment variables (not in code)
- ✅ `.env` file in `.gitignore` (never commit secrets)

---

## Deployment Platforms

### Recommended Combinations

| Backend | Frontend | Database | Cost |
|---------|----------|----------|------|
| Heroku | Netlify | Heroku Postgres | Free tier available |
| DigitalOcean | Vercel | DigitalOcean Managed DB | ~$5-12/mo |
| AWS Elastic Beanstalk | AWS S3+CloudFront | AWS RDS | Pay as you go |
| Render | Render Static | Render PostgreSQL | Free tier available |

---

## Troubleshooting

### Backend Issues

**500 Internal Server Error**:
- Check `heroku logs --tail` or platform logs
- Verify all environment variables are set
- Ensure migrations have run: `python manage.py migrate`

**Database Connection Failed**:
- Verify `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Check database is running and accessible
- Verify firewall rules allow connection

**Static Files Not Loading**:
- Run `python manage.py collectstatic`
- Verify `STATIC_ROOT` and `STATIC_URL` settings
- Check WhiteNoise is in `MIDDLEWARE`

### Frontend Issues

**API Requests Failing**:
- Verify `VITE_API_BASE_URL` is correct
- Check CORS is configured on backend
- Ensure backend domain is in `CORS_ALLOWED_ORIGINS`

**Build Failing**:
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version matches requirements
- Verify all dependencies in `package.json`

**Environment Variables Not Working**:
- Rebuild the app after changing environment variables
- Ensure variables are prefixed with `VITE_`
- Check platform-specific env variable configuration

---

## CI/CD (Future Enhancement)

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v1.2
        with:
          publish-dir: './frontend/dist'
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "Deploy from GitHub Actions"
```

---

## Additional Resources

- **Django Deployment Checklist**: https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
- **Vite Deployment**: https://vitejs.dev/guide/static-deploy.html
- **Heroku Python Guide**: https://devcenter.heroku.com/articles/getting-started-with-python
- **WhiteNoise Documentation**: http://whitenoise.evans.io/en/stable/

---

## Support

For deployment issues or questions, please:
1. Check the troubleshooting section above
2. Review platform-specific documentation
3. Check application logs for error details
4. Open an issue on the GitHub repository

---

**Last Updated**: November 2025
