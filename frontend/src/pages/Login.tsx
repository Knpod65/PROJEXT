import { useEffect, useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useAuth } from "@/store/auth.store";
import { getDefaultRoute } from "@/utils/roles";

export function LoginPage() {
  const { signIn, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      navigate(getDefaultRoute(user), { replace: true });
    }
  }, [navigate, user]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const signedInUser = await signIn(username, password);
      const target = (location.state as { from?: string } | null)?.from ?? getDefaultRoute(signedInUser);
      navigate(target || "/dashboard", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "เข้าสู่ระบบไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <Card className="login-card">
        <div className="login-card__brand">
          <div className="login-card__logo">EMS</div>
          <div>
            <h1>ระบบจัดการข้อสอบ</h1>
            <p>คณะรัฐศาสตร์และรัฐประศาสนศาสตร์ มช.</p>
          </div>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>ชื่อผู้ใช้</span>
            <input
              autoComplete="username"
              onChange={(event) => setUsername(event.target.value)}
              placeholder="firstname.lastname"
              required
              value={username}
            />
          </label>

          <label className="form-field">
            <span>รหัสผ่าน</span>
            <input
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              required
              type="password"
              value={password}
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <Button fullWidth loading={loading} type="submit">
            เข้าสู่ระบบ
          </Button>
          <Button
            fullWidth
            type="button"
            variant="outline"
            onClick={() => {
              window.location.href = "/api/auth/sso/login";
            }}
          >
            เข้าสู่ระบบด้วย CMU SSO
          </Button>
        </form>
      </Card>
    </div>
  );
}
