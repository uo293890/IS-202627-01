import dns.resolver

dominio = "apple.com"

print("Consultando direcciones IP de:", dominio)

try:
    respuesta = dns.resolver.resolve(dominio, "A")

    print("\nDirecciones IPv4 encontradas:")

    for registro in respuesta:
        print(registro.address)

except dns.resolver.NXDOMAIN:
    print("El dominio no existe.")

except dns.resolver.NoAnswer:
    print("El dominio no tiene registros A.")

except dns.resolver.Timeout:
    print("Se ha agotado el tiempo de espera.")

except dns.resolver.DNSException as error:
    print("Error DNS:", error)
