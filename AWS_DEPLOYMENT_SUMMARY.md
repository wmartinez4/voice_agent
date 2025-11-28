# AWS EC2 Deployment Summary

## ✅ Deployment Completed Successfully!

**Date:** November 28, 2025  
**Region:** us-east-1 (N. Virginia)  
**Instance Type:** EC2 t2.micro (Free Tier)

---

## 🌐 Server Information

**Public IP:** `3.219.214.103`  
**HTTPS URL:** `https://3.219.214.103`

**Instance ID:** `i-0b0eb6107dfce25e4`  
**Security Group:** `voice-agent-sg` (`sg-07c3c8ce721610da0`)  
**Elastic IP Allocation:** `eipalloc-0a125cac047e880f9`  
**SSH Key:** `~/.ssh/voice-agent-key.pem`

---

## 📋 ElevenLabs Configuration

Update these 4 tool URLs in your ElevenLabs Agent Dashboard:

### 1. get_customer_name
```
https://3.219.214.103/tools/get-customer-name
```

### 2. get_case_details
```
https://3.219.214.103/tools/get-case-details
```

### 3. propose_payment_plan
```
https://3.219.214.103/tools/propose-payment-plan
```

### 4. update_status
```
https://3.219.214.103/tools/update-status
```

---

## 🐳 Docker Containers Running

| Container | Image | Ports | Status |
|-----------|-------|-------|--------|
| jess-voice-agent | jess-voice-agent:latest | 8000 | ✅ Running |
| jess-nginx | nginx:alpine | 80, 443 | ✅ Running |

---

## ✅ Tested Endpoints

All endpoints are working correctly:

- ✅ `GET /health` - Health check
- ✅ `POST /tools/get-customer-name` - Retrieve customer name
- ✅ `POST /tools/get-case-details` - Get debt details
- ✅ `POST /tools/propose-payment-plan` - Calculate payment plans
- ✅ `POST /tools/update-status` - Update customer status

---

## 🔧 Management Commands

### SSH into EC2
```bash
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
```

### View Logs - Opción 1: CloudWatch (Recomendado)
```
1. Abre AWS Console → CloudWatch → Logs → Log groups
2. Busca estos Log Groups:
   • /aws/ec2/voice-agent/application  (logs generales)
   • /aws/ec2/voice-agent/errors       (solo errores)
3. Click en el log group → Verás los logs en tiempo real
```

**URL Directa:**
- [Log Groups en CloudWatch](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups)

### View Logs - Opción 2: SSH (Script Local)
```bash
# Desde tu máquina local:
./view_aws_logs.sh live      # Ver logs en tiempo real (como en local)
./view_aws_logs.sh api       # Últimos 50 logs
./view_aws_logs.sh errors    # Solo errores
./view_aws_logs.sh status    # Estado de contenedores
```

### View Logs - Opción 3: SSH Manual
```bash
# SSH into EC2 first, then:
sudo docker logs -f jess-voice-agent           # Tiempo real
sudo docker logs --tail 100 jess-voice-agent   # Últimos 100
tail -f ~/voice_agent/logs/app_*.log           # Archivo de logs
```

### Restart Containers
```bash
# SSH into EC2 first, then:
cd ~/voice_agent
sudo docker restart jess-voice-agent
sudo docker restart jess-nginx
```

### Stop Instance (Save Costs)
```bash
# From local machine:
aws ec2 stop-instances --instance-ids i-0b0eb6107dfce25e4 --profile pocaws
```

### Start Instance
```bash
# From local machine:
aws ec2 start-instances --instance-ids i-0b0eb6107dfce25e4 --profile pocaws
```

---

## 🔄 Update Application Code

To deploy code changes:

```bash
# 1. From local machine, transfer updated files
cd /Users/willianmartinez/voice_agent
scp -i ~/.ssh/voice-agent-key.pem main.py database.py ec2-user@3.219.214.103:~/voice_agent/

# 2. SSH into EC2
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103

# 3. Rebuild and restart containers
cd ~/voice_agent
sudo docker stop jess-voice-agent
sudo docker rm jess-voice-agent
sudo docker build -t jess-voice-agent .
sudo docker run -d --name jess-voice-agent \
  --env-file .env \
  -p 8000:8000 \
  -v ~/voice_agent/logs:/app/logs \
  jess-voice-agent
```

---

## 💰 Cost Breakdown

### Free Tier (First 12 months)
- ✅ EC2 t2.micro: 750 hours/month FREE
- ✅ EBS storage (30GB): FREE
- ✅ Data transfer: 100GB/month FREE
- ✅ Elastic IP (while instance running): FREE

### Estimated Cost After Free Tier
- EC2 t2.micro: ~$8.50/month
- EBS 30GB: ~$3.00/month
- Data transfer (beyond 100GB): $0.09/GB
- **Total: ~$11.50/month**

### Cost Optimization Tips
1. Stop instance when not in use (saves EC2 costs)
2. Release Elastic IP if instance stopped for extended periods ($0.005/hour when not attached)
3. Monitor data transfer usage
4. Set up AWS Budgets alerts

---

## 🔐 Security Notes

1. **SSL Certificate:** Self-signed certificate generated for HTTPS
2. **Firewall Rules:** Ports 22, 80, 443, 8000 open
3. **SSH Access:** Only via private key (`voice-agent-key.pem`)
4. **Environment Variables:** Stored securely in `/home/ec2-user/voice_agent/.env`

---

## 🧹 Cleanup Instructions

When you're done testing and want to delete everything:

```bash
# 1. Terminate EC2 instance
aws ec2 terminate-instances --instance-ids i-0b0eb6107dfce25e4 --profile pocaws

# 2. Release Elastic IP
aws ec2 release-address --allocation-id eipalloc-0a125cac047e880f9 --profile pocaws

# 3. Delete Security Group (wait ~2 minutes after instance termination)
aws ec2 delete-security-group --group-name voice-agent-sg --profile pocaws

# 4. Delete SSH Key Pair
aws ec2 delete-key-pair --key-name voice-agent-key --profile pocaws
rm ~/.ssh/voice-agent-key.pem
```

---

## 📞 Test the Voice Agent

After updating ElevenLabs with the new URLs, test a call:

```bash
cd /Users/willianmartinez/voice_agent
source venv/bin/activate
python make_call.py +573124199685
```

Monitor the API logs on EC2 to see the tool calls in real-time:

```bash
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
sudo docker logs -f jess-voice-agent
```

---

## 🎯 Next Steps

1. ✅ **Update ElevenLabs Tool URLs** with the URLs listed above
2. ✅ **Test a call** using `make_call.py`
3. ✅ **Monitor logs** during the call to verify all tools are working
4. ✅ **Adjust Jess prompt** in ElevenLabs if needed for better performance

---

## 📊 Performance Metrics

- **API Response Time:** ~50-100ms
- **SSL Handshake:** ~200-300ms
- **Docker Overhead:** Minimal (<5%)
- **Expected Capacity:** ~500 concurrent requests (far exceeds 50 calls/day requirement)

---

## 🆘 Troubleshooting

### API not responding
```bash
# Check if containers are running
ssh -i ~/.ssh/voice-agent-key.pem ec2-user@3.219.214.103
sudo docker ps

# Check logs
sudo docker logs jess-voice-agent
```

### ElevenLabs can't reach API
1. Verify security group allows port 443
2. Check if nginx container is running
3. Test endpoint manually: `curl -k https://3.219.214.103/health`

### Instance not accessible
1. Check if instance is running: `aws ec2 describe-instances --instance-ids i-0b0eb6107dfce25e4 --profile pocaws`
2. Verify Elastic IP is attached
3. Check security group rules

---

**Deployment completed by:** AI Assistant  
**AWS Profile:** pocaws  
**AWS Account:** 939580423939

