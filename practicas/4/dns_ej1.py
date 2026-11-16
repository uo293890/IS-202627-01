import dns.resolver

dominio = "en.wikipedia.org"

print("Consultando:", dominio)

respuesta = dns.resolver.resolve(dominio, "A")

print("\nPrimera dirección IP:")
print(respuesta[0].address)

print("\nTodas las direcciones IP:")
for registro in respuesta:
    print(registro.address)

print("\nObjeto de respuesta DNS:")
print(respuesta.response)

print("\nMensaje DNS en formato binario:")
print(respuesta.response.to_wire())

print("\nMensaje DNS en hexadecimal:")
print(respuesta.response.to_wire().hex())
