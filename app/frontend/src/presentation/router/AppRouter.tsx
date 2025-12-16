import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Login_Page } from "../pages/Login_Page";
import { Dashboard_Page } from "../pages/Dashboard_Page";
import { Create_Event_Page } from "../pages/Create_Event_Page";
import { Edit_Event_Page } from "../pages/Edit_Event_Page";
import { Event_Detail_Page } from "../pages/Event_Detail_Page";
import { Search_Page } from "../pages/Search_Page";
import { Create_Calendar_Page } from "../pages/Create_Calendar_Page";
import { Edit_Calendar_Page } from "../pages/Edit_Calendar_Page";
import { Calendar_Detail_Page } from "../pages/Calendar_Detail_Page";
import { Settings_Page } from "../pages/Settings_Page";
import { Import_Calendar_Page } from "../pages/Import_Calendar_Page";

const AppRouter = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login_Page />} />
      <Route path="/dashboard" element={<Dashboard_Page />} />
      <Route path="/events/new" element={<Create_Event_Page />} />
      <Route path="/events/:id" element={<Event_Detail_Page />} />
      <Route path="/events/edit/:id" element={<Edit_Event_Page />} />
      <Route path="/calendars/new" element={<Create_Calendar_Page />} />
      <Route path="/calendars/import" element={<Import_Calendar_Page />} />
      <Route path="/calendars/edit/:id" element={<Edit_Calendar_Page />} />
      <Route path="/calendars/:id" element={<Calendar_Detail_Page />} />
      <Route path="/search" element={<Search_Page />} />
      <Route path="/settings" element={<Settings_Page />} />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default AppRouter;
