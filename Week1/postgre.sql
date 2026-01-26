CREATE TABLE IF NOT EXISTS vendors (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  whatsapp VARCHAR(20) NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password VARCHAR(200) NOT NULL,
  logo_url TEXT,
  about TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
  id SERIAL PRIMARY KEY,
  vendor_id INT NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  price NUMERIC(10,2) NOT NULL,
  in_stock BOOLEAN DEFAULT TRUE,
  image_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS delivery_rules (
  id SERIAL PRIMARY KEY,
  vendor_id INT NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  pincode VARCHAR(6) NOT NULL,
  delivery_days INT NOT NULL
);

SELECT * FROM vendors;

-- 1) Add vendor verification fields
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE vendors ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

-- 2) OTP table (secure, time bound)
CREATE TABLE IF NOT EXISTS vendor_otps (
  id SERIAL PRIMARY KEY,
  email VARCHAR(120) NOT NULL,
  otp_hash VARCHAR(200) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Items table - store uploaded image path
ALTER TABLE items ADD COLUMN IF NOT EXISTS image_path TEXT;

ALTER TABLE vendors ADD COLUMN IF NOT EXISTS logo_path TEXT;



