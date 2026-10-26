import asn1tools, sys, pprint
spec = sys.argv[1]
c = asn1tools.compile_files(spec, codec='ber')
raw = open(sys.argv[2],'rb').read()
env = c.decode('EntidadeEnvelopeGenerico', raw)
bu = c.decode('EntidadeBoletimUrna', env['conteudo'])
pprint.pprint({k:v for k,v in env.items() if k!='conteudo'}, width=140)
pprint.pprint(bu, width=140)
