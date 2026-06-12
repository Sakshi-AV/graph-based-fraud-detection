export const seedTransactions = [
  { sender: "C1231006815", receiver: "M1979787155", amount: 9839.64, type: "PAYMENT", risk: 6, prediction: 0 },
  { sender: "C1666544295", receiver: "M2044282225", amount: 1864.28, type: "PAYMENT", risk: 4, prediction: 0 },
  { sender: "C1305486145", receiver: "C553264065", amount: 181.00, type: "TRANSFER", risk: 9, prediction: 0 },
  { sender: "C840083671", receiver: "C38997010", amount: 181.00, type: "CASH_OUT", risk: 11, prediction: 0 },
  { sender: "C905080434", receiver: "C476402209", amount: 215310.30, type: "TRANSFER", risk: 38, prediction: 0 },
  { sender: "C764826684", receiver: "C1825419935", amount: 311685.89, type: "CASH_OUT", risk: 48, prediction: 0 },
  { sender: "C977993101", receiver: "C1983025922", amount: 10000000.00, type: "TRANSFER", risk: 91, prediction: 1 }
];

export const samples = {
  normal: {
    sender: "C1231006815",
    receiver: "M1979787155",
    amount: 9839.64,
    type: "PAYMENT"
  },
  highRisk: {
    sender: "C900000001",
    receiver: "C900000002",
    amount: 725000.00,
    type: "TRANSFER"
  }
};

