import streamlit as st
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import time
import base64

def render_chat_app():
    st.header("🔐 End-to-End Encrypted Chat")
    st.markdown("""
    **How this works (Standard E2EE):**
    1. **User A** and **User B** each generate a **Public Key** (shareable) and a **Private Key** (secret).
    2. To send a message, User A locks it using **User B's Public Key**.
    3. The encrypted message travels over the network (visible as gibberish).
    4. Only **User B's Private Key** can unlock (decrypt) the message.
    """)

    # ---------- KEY GENERATION (Only runs once per session) ----------
    if "keys_generated" not in st.session_state:
        # Generate RSA key pairs for User A
        a_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        st.session_state.a_private = a_private
        st.session_state.a_public = a_private.public_key()
        
        # Generate RSA key pairs for User B
        b_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        st.session_state.b_private = b_private
        st.session_state.b_public = b_private.public_key()
        
        st.session_state.keys_generated = True

    if "a_inbox" not in st.session_state:
        st.session_state.a_inbox = []
    if "b_inbox" not in st.session_state:
        st.session_state.b_inbox = []

    # ---------- ENCRYPTION / DECRYPTION HELPERS ----------
    def encrypt_message(message, public_key):
        ciphertext = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode('utf-8')

    def decrypt_message(ciphertext_b64, private_key):
        try:
            ciphertext = base64.b64decode(ciphertext_b64)
            plaintext = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return plaintext.decode('utf-8')
        except Exception:
            return None

    # ---------- LAYOUT ----------
    col_a, col_b = st.columns(2)

    # ================= USER A =================
    with col_a:
        st.subheader("👤 User A")
        
        msg_a = st.text_area("Message from A → B:", key="msg_a", height=100)
        
        if st.button("🔒 Encrypt & Send to B"):
            if msg_a.strip():
                # User A encrypts using User B's PUBLIC key
                ciphertext = encrypt_message(msg_a, st.session_state.b_public)
                st.session_state.b_inbox.append({
                    "from": "A", "ciphertext": ciphertext, "time": time.strftime("%H:%M:%S")
                })
                st.success("Message encrypted with B's Public Key and delivered.")
            else:
                st.warning("Type a message first.")

        st.markdown("#### 📥 A's Inbox")
        if not st.session_state.a_inbox:
            st.caption("No messages yet.")
        for m in st.session_state.a_inbox:
            # User A decrypts using User A's PRIVATE key
            plain = decrypt_message(m["ciphertext"], st.session_state.a_private)
            if plain:
                st.success(f"[{m['time']}] From {m['from']}: {plain}")
            else:
                st.error("🔒 Cannot decrypt — wrong private key.")

    # ================= USER B =================
    with col_b:
        st.subheader("👤 User B")
        
        msg_b = st.text_area("Message from B → A:", key="msg_b", height=100)
        
        if st.button("🔒 Encrypt & Send to A"):
            if msg_b.strip():
                # User B encrypts using User A's PUBLIC key
                ciphertext = encrypt_message(msg_b, st.session_state.a_public)
                st.session_state.a_inbox.append({
                    "from": "B", "ciphertext": ciphertext, "time": time.strftime("%H:%M:%S")
                })
                st.success("Message encrypted with A's Public Key and delivered.")
            else:
                st.warning("Type a message first.")

        st.markdown("#### 📥 B's Inbox")
        if not st.session_state.b_inbox:
            st.caption("No messages yet.")
        for m in st.session_state.b_inbox:
            # User B decrypts using User B's PRIVATE key
            plain = decrypt_message(m["ciphertext"], st.session_state.b_private)
            if plain:
                st.success(f"[{m['time']}] From {m['from']}: {plain}")
            else:
                st.error("🔒 Cannot decrypt — wrong private key.")

    # ---------- PROOF OF ENCRYPTION (The "Hacker View") ----------
    st.markdown("---")
    st.subheader("🕵️ Network Interception (Proof of E2EE)")
    st.markdown("Check the boxes below to see the exact logical flow of encryption and decryption.")
    
    p1, p2 = st.columns(2)
    
    # USER A TO B LOGIC
    with p1:
        st.markdown("**Message from A → B**")
        if st.checkbox("Show A → B Interception", key="intercept_ab"):
            if st.session_state.b_inbox:
                latest_msg = st.session_state.b_inbox[-1]
                
                # 1. SHOW ENCRYPTED FIRST
                st.markdown("**1. What the network sees (Ciphertext):**")
                st.code(latest_msg["ciphertext"], language="text")
                
                # 2. SHOW PLAINTEXT SECOND
                st.markdown("**2. What User B sees after decrypting (Plaintext):**")
                plain = decrypt_message(latest_msg["ciphertext"], st.session_state.b_private)
                st.success(plain)
            else:
                st.caption("No messages sent yet.")
                
    # USER B TO A LOGIC
    with p2:
        st.markdown("**Message from B → A**")
        if st.checkbox("Show B → A Interception", key="intercept_ba"):
            if st.session_state.a_inbox:
                latest_msg = st.session_state.a_inbox[-1]
                
                # 1. SHOW ENCRYPTED FIRST
                st.markdown("**1. What the network sees (Ciphertext):**")
                st.code(latest_msg["ciphertext"], language="text")
                
                # 2. SHOW PLAINTEXT SECOND
                st.markdown("**2. What User A sees after decrypting (Plaintext):**")
                plain = decrypt_message(latest_msg["ciphertext"], st.session_state.a_private)
                st.success(plain)
            else:
                st.caption("No messages sent yet.")