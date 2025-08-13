import React from 'react';
import './App.css';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    LineChart, Line, PieChart, Pie, Cell, Legend
} from 'recharts';
import dayjs from 'dayjs';
import Header from './components/Header';
import { useState } from 'react';


const Dashboard = ({ platform, setPlatform, movie, setMovie, handleSearch, reviews, id, setID }) => {
    if (!reviews || reviews.length === 0) {
        return (
            <>
                <Header
                    platform={platform}
                    setPlatform={setPlatform}
                    movie={movie}
                    setMovie={setMovie}
                    handleSearch={handleSearch}
                    id={id}
                    setID={setID}
                />
                <Typography variant="h6" align="center" mt={4}>
                    Không có đánh giá nào để hiển thị.
                </Typography>
            </>
        );
    }

    // --- Biểu đồ Line: cảm xúc theo tháng ---
    const monthlySentiment = {};

    reviews.forEach(r => {
        const month = dayjs(r.Date).format('YYYY-MM');
        const sentiment = r.Sentiment?.toLowerCase() || 'neutral';

        if (!monthlySentiment[month]) {
            monthlySentiment[month] = { month, positive: 1, negative: 0 };
        }

        if (sentiment === 'positive') monthlySentiment[month].positive++;
        else if (sentiment === 'negative') monthlySentiment[month].negative++;
        // else monthlySentiment[month].neutral++;
    });

    const lineData = Object.values(monthlySentiment).sort((a, b) =>
        a.month.localeCompare(b.month)
    );

    // --- Biểu đồ Pie: tỷ lệ cảm xúc ---
    const pieData = [
        {
            name: 'Positive',
            value: reviews.filter(r => r.Sentiment === 'POSITIVE').length,
        },
        {
            name: 'Negative',
            value: reviews.filter(r => r.Sentiment === 'NEGATIVE').length,
        },
    ];

    const pieColors = ['#90a955', '#f07167'];

    return (
        <>
            {/* Header tái sử dụng */}
            <Header
                platform={platform}
                setPlatform={setPlatform}
                movie={movie}
                setMovie={setMovie}
                handleSearch={handleSearch}
            />

            {/* Thống kê tổng quan */}
            <Grid container spacing={3} justifyContent="center" padding={3}>
                {/* Biểu đồ Line */}
                <Grid item xs={12} md={10}>
                    <Card className="dashboard-card">
                        <CardContent>
                            <Typography className="dashboard-title">Emotional Damage</Typography>
                            <div className="dashboard-chart-container">
                                <ResponsiveContainer width="50%" height={500}>
                                    <LineChart data={lineData}>
                                        <XAxis dataKey="month" />
                                        <YAxis allowDecimals={false} />
                                        <Tooltip />
                                        <Legend />
                                        <Line type="monotone" dataKey="positive" stroke="#4caf50" name="Positive" />
                                        <Line type="monotone" dataKey="negative" stroke="#f44336" name="Negative" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Biểu đồ Pie */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6">Tỷ lệ cảm xúc tích cực vs tiêu cực</Typography>
                            <ResponsiveContainer width="100%" height={250}>
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        dataKey="value"
                                        nameKey="name"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={80}
                                        label
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid >
        </>
    );
};

export default Dashboard;
