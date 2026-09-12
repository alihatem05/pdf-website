import { Outlet } from "react-router-dom";
import Sidebar from "../sidebar/sidebar.jsx";
import "./mainPage.css";

function MainPage() {
  return (
    <div className="main-page">
      <Sidebar />
      <Outlet />
    </div>
  );
}

export default MainPage;