import os
import tempfile

import certifi

# O servidor não envia o certificado intermediário da GlobalSign,
# então ele é somado ao bundle padrão do certifi.
INTERMEDIATE_CERT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ssl",
    "globalsign_atlas_r3_ov_2026q1.pem",
)


def build_ca_bundle():
    """Cria um bundle com as CAs do certifi + o intermediário que falta"""
    bundle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".pem", prefix="braga_ca_", delete=False
    )
    with bundle, open(certifi.where()) as base, open(INTERMEDIATE_CERT) as extra:
        bundle.write(base.read())
        bundle.write("\n")
        bundle.write(extra.read())
    return bundle.name


CA_BUNDLE = build_ca_bundle()
