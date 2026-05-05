# Field-to-Query Mapping
# We group related fields to reduce the number of Pinecone calls (Efficiency)

QUERY_BUCKETS = {
    "data_collection_and_retention": [
        "What personal data is collected? (email, location, biometrics, usage stats)",
        "How long is user data stored and what are the retention periods?",
        "When is data deleted or anonymized?"
    ],
    "third_party_and_sharing": [
        "Is data shared with third parties, affiliates, or advertising partners?",
        "List specific names of third-party partners or categories of companies.",
        "Are there any data selling practices mentioned?"
    ],
    "security_and_encryption": [
        "What encryption standards are used for data at rest and in transit?",
        "Mention of TLS, SSL, AES-256, or industry standard security protocols.",
        "Are there specific security measures like hashing or salting?"
    ],
    "user_rights_and_opt_out": [
        "Is there an opt-out mechanism for data collection or sharing?",
        "How can a user request data deletion or access their information?",
        "References to GDPR, CCPA, or privacy settings."
    ]
}




QUERY_REGISTRY = {
    "q1.0.0": {
            "data_collection_and_retention": [
            "What personal data is collected? (email, location, biometrics, usage stats)",
            "How long is user data stored and what are the retention periods?",
            "When is data deleted or anonymized?"
        ],
        "third_party_and_sharing": [
            "Is data shared with third parties, affiliates, or advertising partners?",
            "List specific names of third-party partners or categories of companies.",
            "Are there any data selling practices mentioned?"
        ],
        "security_and_encryption": [
            "What encryption standards are used for data at rest and in transit?",
            "Mention of TLS, SSL, AES-256, or industry standard security protocols.",
            "Are there specific security measures like hashing or salting?"
        ],
        "user_rights_and_opt_out": [
            "Is there an opt-out mechanism for data collection or sharing?",
            "How can a user request data deletion or access their information?",
            "References to GDPR, CCPA, or privacy settings."
        ]
    },

    
    "q1.1.0": {
        "buckets": {
            "data_collection": ["Identify flags for email, location, and biometrics specifically."], # More specific
            "security": ["Search for AES-256, TLS, or SSL protocols."] 
        }
    }
}

ACTIVE_QUERY_VERSION = "q1.0.0"