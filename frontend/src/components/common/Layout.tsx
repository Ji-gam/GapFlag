import { NavLink, Outlet } from "react-router-dom";

// 로그인 기능이 필요해지면 로그인/회원가입 링크를 다시 추가한다.
const NAV_ITEMS: { to: string; label: string }[] = [];

// 로그인 필요 라우트 공통 뼈대 — 실제 인증 게이트는 RequireAuth.
export default function Layout() {
  return (
    <div>
      <nav>
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === "/"}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
