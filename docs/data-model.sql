-- 站点与评分
CREATE TABLE sites (
  id BIGSERIAL PRIMARY KEY,
  host TEXT UNIQUE NOT NULL,
  first_seen_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE site_scores (
  site_id BIGINT PRIMARY KEY REFERENCES sites(id),
  score_total NUMERIC NOT NULL,
  score_s NUMERIC NOT NULL,
  score_c NUMERIC NOT NULL,
  score_t NUMERIC NOT NULL,
  score_u NUMERIC NOT NULL,
  signals JSONB NOT NULL,
  model_version TEXT NOT NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 用户与投票
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  handle TEXT UNIQUE,
  email TEXT UNIQUE,
  password_hash TEXT,
  reputation NUMERIC NOT NULL DEFAULT 0,
  roles TEXT[] DEFAULT ARRAY['user'],
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE votes (
  id BIGSERIAL PRIMARY KEY,
  site_id BIGINT REFERENCES sites(id),
  user_id BIGINT REFERENCES users(id),
  label TEXT CHECK (label IN ('safe','suspicious','danger')),
  reason TEXT,
  weight NUMERIC NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(site_id, user_id)
);

-- 论坛
CREATE TABLE posts (
  id BIGSERIAL PRIMARY KEY,
  site_id BIGINT REFERENCES sites(id),
  user_id BIGINT REFERENCES users(id),
  title TEXT, content_md TEXT,
  score INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE comments (
  id BIGSERIAL PRIMARY KEY,
  post_id BIGINT REFERENCES posts(id),
  user_id BIGINT REFERENCES users(id),
  content_md TEXT,
  score INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE reactions (
  id BIGSERIAL PRIMARY KEY,
  target_type TEXT CHECK (target_type IN ('post','comment')),
  target_id BIGINT NOT NULL,
  user_id BIGINT REFERENCES users(id),
  value SMALLINT CHECK (value IN (-1, 1)),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(target_type, target_id, user_id)
);

-- 申诉
CREATE TABLE appeals (
  id BIGSERIAL PRIMARY KEY,
  site_id BIGINT REFERENCES sites(id),
  submitter_email TEXT,
  message TEXT,
  status TEXT CHECK (status IN ('open','reviewing','resolved')) DEFAULT 'open',
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 索引建议
-- site_scores(site_id), votes(site_id), posts(site_id, created_at), comments(post_id, created_at)
-- 反刷：users(reputation), reactions(target_type, target_id)
