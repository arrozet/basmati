import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Login_Page } from '../pages/Login_Page';
import { Dashboard_Page } from '../pages/Dashboard_Page';
import { Create_Event_Page } from '../pages/Create_Event_Page';
import { Search_Page } from '../pages/Search_Page';

const AppRouter = () => {
    return (
        <Routes>
            <Route path="/login" element={<Login_Page />} />
            <Route path="/dashboard" element={<Dashboard_Page />} />
            <Route path="/events/new" element={<Create_Event_Page />} />
            <Route path="/search" element={<Search_Page />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
    );
};

export default AppRouter;
