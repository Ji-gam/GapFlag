import { createBrowserRouter } from "react-router-dom";

import Layout from "./components/common/Layout";
import RequireAuth from "./components/common/RequireAuth";
// 로그인 기능이 필요해지면 아래 두 줄과 라우트 항목의 주석을 해제한다 (auth_kit/README.md 참고).
// import LoginPage from "./pages/LoginPage/LoginPage";
// import SignupPage from "./pages/SignupPage/SignupPage";

// 도메인 화면(페이지)은 src/pages 아래에 추가하고 여기에 라우트를 등록한다.
// 로그인 필요 라우트는 Layout 하위 RequireAuth로 감싼다.
export const router = createBrowserRouter([
  { path: "/", element: <div>GapFlag</div> },
  // { path: "/login", element: <LoginPage /> },
  // { path: "/signup", element: <SignupPage /> },
  {
    element: <Layout />,
    children: [
      {
        element: <RequireAuth />,
        children: [],
      },
    ],
  },
]);
