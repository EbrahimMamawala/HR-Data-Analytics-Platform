// app/api/diversity/trends/route.ts
import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";

export async function GET() {
  const { db } = await connectToDatabase();
  const collection = db.collection("Diversity");

  // Calculate last 5 months from current
  const months = [];
  const currentDate = new Date();
  for (let i = 0; i < 5; i++) {
    const date = new Date(currentDate);
    date.setMonth(date.getMonth() - i);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    months.push(`${year}-${month}`);
  }

  // Fetch data for these months
  const data = await collection.find({
    frequency: "month",
    period: { $in: months }
  }).toArray();

  // Create default data structure
  const defaultData = months.map(period => ({
    period,
    male: 0,
    female: 0,
    other: 0
  }));

  // Merge database data with default values
  const mergedData = defaultData.map(item => {
    const dbItem = data.find((d: any) => d.period === item.period);
    return {
      ...item,
      male: dbItem?.gender_distribution?.Male || 0,
      female: dbItem?.gender_distribution?.Female || 0,
      other: dbItem?.gender_distribution?.Other || 0,
    };
  });

  // Sort by date ascending
  const sortedData = mergedData.sort((a, b) => 
    a.period.localeCompare(b.period)
  );

  return NextResponse.json(sortedData);
}