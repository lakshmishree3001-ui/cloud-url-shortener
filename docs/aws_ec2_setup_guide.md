# AWS EC2 Cloud Setup Guide for URL Shortener

This guide walks you through launching a Free-Tier **AWS EC2 Virtual Server**, configuring network firewall rules for FastAPI, and connecting directly to your cloud environment.

---

## 1. Where to Go & What to Click in the AWS Console

### Step 1: Open the EC2 Dashboard
1. Log into your AWS account at: [**https://aws.amazon.com/console/**](https://aws.amazon.com/console/)
2. In the top search bar, type: **`EC2`** and click on **EC2 (Virtual Servers in the Cloud)**.
3. Make sure your region (top-right corner) is selected (e.g., `us-east-1` (N. Virginia), `ap-south-1` (Mumbai), or `us-west-2` (Oregon)).

---

### Step 2: Launch a New Free-Tier EC2 Instance
1. In the EC2 dashboard, click the orange **Launch instance** button.
2. **Name and tags**:
   - Name: `url-shortener-server`
3. **Application and OS Images (Amazon Machine Image)**:
   - Select **Ubuntu** (Ubuntu Server 24.04 LTS or 22.04 LTS, 64-bit x86).
   - Ensure the label says **Free tier eligible**.
4. **Instance type**:
   - Choose `t2.micro` (or `t3.micro` if in regions where `t3` is the free tier default).
   - Ensure it says **Free tier eligible**.
5. **Key pair (login)**:
   - Click **Create new key pair**.
   - Key pair name: `url-shortener-key`
   - Key pair type: `RSA`
   - Private key file format: `.pem`
   - Click **Create key pair** (a `.pem` file will download to your `Downloads` folder).

---

### Step 3: Configure Network Firewall (Security Group)
*This is the most critical step so your FastAPI server can accept HTTP and Port 8000 traffic!*

1. Under **Network settings**, click **Edit** (top right of that section).
2. Ensure **Auto-assign public IP** is set to **Enable**.
3. Under **Firewall (security groups)**:
   - Select **Create security group**.
   - Security group name: `url-shortener-sg`.
   - Description: `Allow SSH, HTTP, and FastAPI Port 8000`.
4. Check or add the following 3 firewall rules:
   - **Rule 1 (SSH)**:
     - Type: `SSH` | Port: `22` | Source: `Anywhere (0.0.0.0/0)` or `My IP`
   - **Rule 2 (HTTP)**:
     - Click **Add security group rule**
     - Type: `HTTP` | Port: `80` | Source: `Anywhere (0.0.0.0/0)`
   - **Rule 3 (FastAPI Custom TCP)**:
     - Click **Add security group rule**
     - Type: `Custom TCP` | Port: `8000` | Source: `Anywhere (0.0.0.0/0)`
5. **Configure storage**: Leave at default (8 GiB gp3, Free tier).
6. Click the orange **Launch instance** button at the bottom right!

---

## 2. Connecting to Your EC2 Instance (Zero Setup!)

Wait about 30 seconds until the **Instance state** displays **Running**.

1. In the EC2 instances list, click the checkmark next to your instance (`url-shortener-server`).
2. Click the **Connect** button at the top.
3. In the tabs at the top, select **EC2 Instance Connect**.
4. Leave username as `ubuntu`.
5. Click the orange **Connect** button!
6. A black Linux terminal will open **directly in your browser window**! You are now inside your AWS Cloud Server!

---

## 3. Setting Up the Project in AWS

Once inside your EC2 terminal in the browser, run these commands to set up the environment and fetch the project code:

```bash
# 1. Update packages
sudo apt update -y && sudo apt install -y python3-pip python3-venv git curl unzip

# 2. Create the project folder
mkdir -p ~/cloud-url-shortener
cd ~/cloud-url-shortener
```

Now you are running directly on AWS!
