import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/login", label: "로그인" },
  { to: "/signup", label: "회원가입" },
];

// 로그인 필요 라우트 공통 뼈대 — 실제 인증 게이트(RequireAuth)는 T-ACC-1 프론트 연동 시 추가.
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
