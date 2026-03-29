export const INDIAN_SYMBOL_SUGGESTIONS = [
  'RELIANCE',
  'TCS',
  'INFY',
  'HDFCBANK',
  'ICICIBANK',
  'LT',
  'SBIN',
  'BHARTIARTL',
  'ITC',
  'AXISBANK',
];

const SYMBOL_PATTERN = /^[A-Z0-9]{1,12}(\.NS)?$/;
const COMMON_NON_INDIAN_SYMBOLS = new Set([
  'AAPL',
  'MSFT',
  'NVDA',
  'AMZN',
  'GOOGL',
  'GOOG',
  'META',
  'TSLA',
  'AMD',
  'NFLX',
]);

export function normalizeIndianSymbol(value) {
  const raw = value.trim().toUpperCase();
  if (!raw) {
    return '';
  }

  if (!SYMBOL_PATTERN.test(raw)) {
    throw new Error('Use Indian NSE symbols only, like RELIANCE or RELIANCE.NS.');
  }

  if (raw.includes('.') && !raw.endsWith('.NS')) {
    throw new Error('Only NSE-format symbols are supported. Use RELIANCE or RELIANCE.NS.');
  }

  const base = raw.endsWith('.NS') ? raw.slice(0, -3) : raw;
  if (COMMON_NON_INDIAN_SYMBOLS.has(base)) {
    throw new Error('Non-Indian stocks are not supported. Use NSE symbols like RELIANCE, TCS, or INFY.');
  }

  return raw.endsWith('.NS') ? raw : `${raw}.NS`;
}

export function normalizeIndianSymbolList(value) {
  const items = value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

  if (!items.length) {
    return '';
  }

  return items.map(normalizeIndianSymbol).join(',');
}
