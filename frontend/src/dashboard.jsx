import React from 'react';
import './App.css';
import { Grid, Card, CardContent, Typography, Box } from '@mui/material';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    LineChart, Line, PieChart, Pie, Cell, Legend
} from 'recharts';
import dayjs from 'dayjs';
import Header from './components/Header';
import { useState } from 'react';
import { useParams } from 'react-router-dom';

// // Fake data with multiple months of reviews
// const fakeFilm = {
//     Title: 'Fake Film',
//     Date: '2023-06-15',
//     Platform: 'rotten_tomatoes',
//     imdbID: 'tt1234567',
//     Reviews: [
//         // ---- 2023-06 ---------------------------------------------------
//         { Date: '2023-06-05', Sentiment: 'POSITIVE' },
//         { Date: '2023-06-08', Sentiment: 'NEGATIVE' },
//         { Date: '2023-06-12', Sentiment: 'POSITIVE' },

//         // ---- 2023-07 ---------------------------------------------------
//         { Date: '2023-07-03', Sentiment: 'NEGATIVE' },
//         { Date: '2023-07-10', Sentiment: 'NEGATIVE' },
//         { Date: '2023-07-21', Sentiment: 'POSITIVE' },

//         // ---- 2023-08 ---------------------------------------------------
//         { Date: '2023-08-02', Sentiment: 'POSITIVE' },
//         { Date: '2023-08-11', Sentiment: 'POSITIVE' },
//         { Date: '2023-08-22', Sentiment: 'NEGATIVE' },

//         // ---- 2023-09 ---------------------------------------------------
//         { Date: '2023-09-04', Sentiment: 'POSITIVE' },
//         { Date: '2023-09-09', Sentiment: 'POSITIVE' },
//         { Date: '2023-09-19', Sentiment: 'NEGATIVE' },

//         // ---- 2023-10 ---------------------------------------------------
//         { Date: '2023-10-01', Sentiment: 'POSITIVE' },
//         { Date: '2023-10-02', Sentiment: 'NEGATIVE' },
//         { Date: '2023-10-03', Sentiment: 'POSITIVE' },
//         { Date: '2023-10-15', Sentiment: 'POSITIVE' },
//         { Date: '2023-10-28', Sentiment: 'NEGATIVE' },

//         // ---- 2023-11 ---------------------------------------------------
//         { Date: '2023-11-06', Sentiment: 'NEGATIVE' },
//         { Date: '2023-11-17', Sentiment: 'NEGATIVE' },
//         { Date: '2023-11-23', Sentiment: 'POSITIVE' },

//         // ---- 2023-12 ---------------------------------------------------
//         { Date: '2023-12-02', Sentiment: 'POSITIVE' },
//         { Date: '2023-12-14', Sentiment: 'POSITIVE' },
//         { Date: '2023-12-27', Sentiment: 'NEGATIVE' },

//         // ---- 2024-01 ---------------------------------------------------
//         { Date: '2024-01-05', Sentiment: 'POSITIVE' },
//         { Date: '2024-01-20', Sentiment: 'NEGATIVE' }
//     ]
// };

// const reviews = fakeFilm.Reviews || [];

const Dashboard = ({ platform, setPlatform, movie, setMovie, handleSearch }) => {
    const { movieId } = useParams();
    if (!reviews || reviews.length === 0) {
        return (
            <>
                <Header
                    platform={platform}
                    setPlatform={setPlatform}
                    movie={movie}
                    setMovie={setMovie}
                    handleSearch={handleSearch}
                    id={movieId}
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
            monthlySentiment[month] = { month, positive: 0, negative: 0 };
        }

        if (sentiment === 'positive') monthlySentiment[month].positive++;
        else if (sentiment === 'negative') monthlySentiment[month].negative++;
    });

    const lineData = Object.keys(monthlySentiment)
        .sort()
        .map(month => ({
            month,
            positive: monthlySentiment[month].positive,
            negative: monthlySentiment[month].negative,
        }));

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
            {/* reuse Header */}
            <Header
                platform={platform}
                setPlatform={setPlatform}
                movie={movie}
                setMovie={setMovie}
                handleSearch={handleSearch}
            />

            <Grid
                container
                direction="column"
                alignItems="center"
                spacing={4}
                padding={3}
                sx={{ width: '100%' }}
            >
                {/* ───── LINE CHART ───── */}
                <Grid item sx={{ width: '80%' }}>
                    <Card>
                        <CardContent>
                            <Typography align="center" variant="h6" mb={2}>
                                Emotional Damage
                            </Typography>

                            <ResponsiveContainer width="100%" height={350}>
                                <LineChart data={lineData}>
                                    <XAxis
                                        dataKey="month"
                                        interval={0}
                                        angle={-40}
                                        textAnchor="end"
                                        height={60}
                                    />
                                    <YAxis allowDecimals={false} />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="positive" stroke="#4caf50" />
                                    <Line type="monotone" dataKey="negative" stroke="#f44336" />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* ───── PIE CHART ───── */}
                <Grid item sx={{ width: '80%' }}>
                    <Card>
                        <CardContent>
                            <Typography align="center" variant="h6" mb={2}>
                                Tỷ lệ cảm xúc tích cực vs tiêu cực
                            </Typography>

                            <ResponsiveContainer width="100%" height={350}>
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        dataKey="value"
                                        nameKey="name"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={110}
                                        label
                                    >
                                        {pieData.map((_, i) => (
                                            <Cell key={i} fill={pieColors[i % pieColors.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </>
    );
};

export default Dashboard;
