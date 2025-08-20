# Halls Booking App - Deployment Guide

This guide provides step-by-step instructions for deploying both the Flask backend and React frontend of the Halls Booking application.

## 🚀 Backend Deployment

### Option 1: Deploy to Heroku (Recommended for beginners)

1. **Create a Heroku account** at [heroku.com](https://heroku.com)

2. **Install Heroku CLI** from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

3. **Login to Heroku**:
   ```bash
   heroku login
   ```

4. **Create a new Heroku app**:
   ```bash
   heroku create your-halls-booking-api
   ```

5. **Set up MongoDB Atlas** (Free tier):
   - Go to [mongodb.com/atlas](https://mongodb.com/atlas)
   - Create a free account and cluster
   - Get your connection string (replace `<password>` with your actual password)
   - Whitelist all IPs (0.0.0.0/0) for Heroku deployment

6. **Configure environment variables on Heroku**:
   ```bash
   heroku config:set MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/halls_db?retryWrites=true&w=majority"
   heroku config:set JWT_SECRET="your-super-secure-jwt-secret-key"
   heroku config:set SMTP_HOST="smtp.gmail.com"
   heroku config:set SMTP_PORT="587"
   heroku config:set SMTP_USER="your-email@gmail.com"
   heroku config:set SMTP_PASS="your-app-password"
   heroku config:set SMTP_FROM="your-email@gmail.com"
   heroku config:set APP_URL="https://your-frontend-domain.netlify.app"
   heroku config:set GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
   ```

7. **Deploy to Heroku**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

8. **Your API will be available at**: `https://your-halls-booking-api.herokuapp.com`

### Option 2: Deploy to Railway

1. **Create account** at [railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Add environment variables** in Railway dashboard
4. **Deploy automatically** from GitHub

### Option 3: Deploy to Render

1. **Create account** at [render.com](https://render.com)
2. **Create new Web Service** from GitHub
3. **Configure build and start commands**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. **Add environment variables** in Render dashboard

## 🌐 Frontend Deployment

### Option 1: Deploy to Netlify (Recommended)

1. **Create account** at [netlify.com](https://netlify.com)

2. **Install Netlify CLI** (optional):
   ```bash
   npm install -g netlify-cli
   ```

3. **Build the frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Deploy via drag-and-drop**:
   - Go to Netlify dashboard
   - Drag the `frontend/dist` folder to deploy
   - Or connect your GitHub repository for automatic deployments

5. **Configure environment variables** in Netlify:
   - Go to Site settings > Environment variables
   - Add: `VITE_API_BASE_URL=https://your-halls-booking-api.herokuapp.com`
   - Add: `VITE_GOOGLE_CLIENT_ID=your-google-client-id`

6. **Configure redirects** (already included in `netlify.toml`)

### Option 2: Deploy to Vercel

1. **Create account** at [vercel.com](https://vercel.com)
2. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```
3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```
4. **Add environment variables** in Vercel dashboard

### Option 3: Deploy to AWS S3 + CloudFront

1. **Create S3 bucket** with static website hosting
2. **Build and upload**:
   ```bash
   cd frontend
   npm run build
   aws s3 sync dist/ s3://your-bucket-name
   ```
3. **Configure CloudFront** for HTTPS and caching

## 🔧 Database Setup (MongoDB Atlas)

1. **Create MongoDB Atlas account** at [mongodb.com/atlas](https://mongodb.com/atlas)

2. **Create a new cluster** (free tier M0)

3. **Create database user**:
   - Go to Database Access
   - Add new database user with read/write permissions

4. **Configure network access**:
   - Go to Network Access
   - Add IP address: `0.0.0.0/0` (allow from anywhere)

5. **Get connection string**:
   - Go to Clusters > Connect > Connect your application
   - Copy the connection string
   - Replace `<password>` with your database user password

6. **Create database and collections**:
   The Flask app will automatically create collections when first used.

## 🔐 Environment Variables

### Backend (.env or Heroku Config Vars)
```bash
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/halls_db
JWT_SECRET=your-super-secure-jwt-secret-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@gmail.com
APP_URL=https://your-frontend-domain.netlify.app
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### Frontend (.env or Netlify Environment Variables)
```bash
VITE_API_BASE_URL=https://your-halls-booking-api.herokuapp.com
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

## 🧪 Testing Deployment

### Test Backend APIs
```bash
# Health check
curl https://your-halls-booking-api.herokuapp.com/health

# Test signup
curl -X POST https://your-halls-booking-api.herokuapp.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","is_venue_owner":false}'
```

### Test Frontend
1. Visit your deployed frontend URL
2. Test user registration and login
3. Test venue search functionality
4. Verify API communication

## 📊 Monitoring and Logging

### Backend Monitoring
- **Heroku**: Use Heroku logs (`heroku logs --tail`)
- **Railway**: Built-in logging dashboard
- **Render**: Logs available in dashboard

### Frontend Monitoring
- **Netlify**: Deploy logs and function logs
- **Vercel**: Real-time logs and analytics
- **CloudWatch**: For AWS deployments

## 🔒 Security Considerations

1. **HTTPS**: Ensure both frontend and backend use HTTPS
2. **CORS**: Configure CORS properly for your frontend domain
3. **Environment Variables**: Never commit secrets to version control
4. **Database**: Use strong passwords and limit network access
5. **JWT Secret**: Use a strong, random JWT secret key

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Update CORS configuration in Flask app
   - Add your frontend domain to allowed origins

2. **Database Connection**:
   - Check MongoDB Atlas network access settings
   - Verify connection string format

3. **Environment Variables**:
   - Ensure all required variables are set
   - Check variable names match exactly

4. **Build Failures**:
   - Check Node.js version compatibility
   - Verify all dependencies are installed

### Getting Help

1. Check application logs
2. Verify environment variables
3. Test API endpoints individually
4. Check network connectivity
5. Review deployment platform documentation

## 📝 Post-Deployment Checklist

- [ ] Backend API is accessible and returns health check
- [ ] Database connection is working
- [ ] Frontend loads without errors
- [ ] User registration/login works
- [ ] Venue search functionality works
- [ ] CORS is properly configured
- [ ] Environment variables are set correctly
- [ ] HTTPS is enabled on both frontend and backend
- [ ] Error handling works as expected
- [ ] Email functionality works (if SMTP is configured)

## 🔄 Continuous Deployment

### GitHub Actions (Optional)
Create `.github/workflows/deploy.yml` for automated deployments:

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-halls-booking-api"
          heroku_email: "your-email@example.com"
```

This completes the deployment guide. Your Halls Booking application should now be live and accessible to users worldwide!