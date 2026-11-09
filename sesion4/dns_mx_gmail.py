import dns.resolver


dominio = "gmail.com"

print("Servidores MX de", dominio)

try:
    respuesta = dns.resolver.resolve(dominio, "MX")

    servidores = []

    for registro in respuesta:
        preferencia = registro.preference
        servidor = str(registro.exchange).rstrip(".")

        servidores.append((preferencia, servidor))

    servidores.sort()

    for preferencia, servidor in servidores:
        print("\nPreferencia:", preferencia)
        print("Servidor:", servidor)

        try:
            ips = dns.resolver.resolve(servidor, "A")

            print("Direcciones IPv4:")

            for ip in ips:
                print(" ", ip.address)

        except dns.resolver.DNSException as error:
            print("No se pudieron obtener las IPv4:", error)

        try:
            ips6 = dns.resolver.resolve(servidor, "AAAA")

            print("Direcciones IPv6:")

            for ip in ips6:
                print(" ", ip.address)

        except dns.resolver.DNSException:
            pass

except dns.resolver.DNSException as error:
    print("Error DNS:", error)
