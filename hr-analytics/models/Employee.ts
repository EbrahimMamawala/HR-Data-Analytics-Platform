import mongoose from "mongoose";

const EmployeeSchema = new mongoose.Schema({
  EmployeeID: Number,
  Age: Number,
  Department: String,
  Email: String,
  FirstName: String,
  LastName: String,
  Gender: String,
  JoinDate: String,
  Position: String,
  Status: String,
},{ 
    collection: 'Employees'
});

export default mongoose.models.Employee || mongoose.model("Employees", EmployeeSchema);