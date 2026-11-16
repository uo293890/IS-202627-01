docker run --name amigos2.0 \
   -e DEPLOYMENT_MODE=production \
   -e DATABASE_URI=mysql+pymysql://amigosuser:amigospass@basedatos/amigosdb \
   --rm -d --network pruebas amigos:2.0