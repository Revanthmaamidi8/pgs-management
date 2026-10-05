import { useEffect, useState } from 'react'
import axios from 'axios'
import { Navigate, Route, Routes } from 'react-router-dom'
import { BrowserRouter } from 'react-router-dom'

type User = {
  id: string
  username: string
  email: string
  full_name: string
  role?: string
}

type PGRecord = {
  id: string
  name: string
  city: string
  address: string
  number_of_floors: number
  is_active: boolean
}

type RoomRecord = {
  id: string
  pg_property_id: string
  room_number: string
  floor: number
  room_type: string
  capacity: number
  monthly_rent: number
  status: string
}

type TenantRecord = {
  id: string
  pg_property_id: string
  full_name: string
  status: string
  deposit_amount: number
}

type TenantDetailsRecord = TenantRecord & {
  pg_property_name: string
  phone_number: string
  email: string | null
  date_of_birth: string | null
  gender: string | null
  address: string | null
  emergency_contact: string | null
  emergency_phone: string | null
  government_id_type: string | null
  government_id_number: string | null
  joining_date: string
  expected_leaving_date: string | null
  actual_leaving_date: string | null
  is_active: boolean
}

type BedRecord = {
  id: string
  room_id: string
  bed_number: string
  status: string
}

type AllocationRecord = {
  id: string
  tenant_id: string
  bed_id: string
  pg_property_id: string
  start_date: string
  end_date?: string | null
  status: string
  is_active: boolean
  notes?: string | null
}

type RentRecord = {
  id: string
  tenant_id: string
  pg_property_id: string
  month: string
  amount: number
  due_date: string
  paid_amount: number
  status: string
  notes?: string | null
}

type PaymentRecord = {
  id: string
  tenant_id: string
  pg_property_id: string
  rent_record_id?: string | null
  amount: number
  payment_date: string
  payment_mode: string
  reference_number?: string | null
  status: string
  notes?: string | null
}

type DepositRecord = {
  id: string
  tenant_id: string
  pg_property_id: string
  amount: number
  deposit_date: string
  payment_mode: string
  reference_number?: string | null
  status: string
  notes?: string | null
}

type ExpenseRecord = {
  id: string
  pg_property_id: string
  category: string
  description: string
  amount: number
  expense_date: string
  vendor?: string | null
  payment_mode: string
  reference_number?: string | null
  status: string
  notes?: string | null
}

type OccupancyRow = {
  name: string
  rooms: number
  occupied: number
  vacancy: number
}

type PGForm = {
  name: string
  address: string
  city: string
  state: string
  pincode: string
  contact_number: string
  email: string
  number_of_floors: number
  description: string
  facilities: string
}

type RoomForm = {
  pg_property_id: string
  room_number: string
  floor: number
  room_type: string
  capacity: number
  monthly_rent: number
  status: string
  description: string
}

type TenantForm = {
  pg_property_id: string
  full_name: string
  phone_number: string
  email: string
  date_of_birth: string
  gender: string
  address: string
  emergency_contact: string
  emergency_phone: string
  government_id_type: string
  government_id_number: string
  joining_date: string
  expected_leaving_date: string
  actual_leaving_date: string
  deposit_amount: number
  status: string
}

const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use((config) => {
  config.headers.delete('Authorization')
  config.headers.set('X-Portal-Role', localStorage.getItem('pg_portal_role') ?? 'OWNER')
  return config
})

const defaultStatCards = [
  { label: 'PGs', value: '0', detail: 'No properties yet' },
  { label: 'Rooms', value: '0', detail: 'No room data yet' },
  { label: 'Tenants', value: '0', detail: 'No tenants yet' },
  { label: 'Occupancy', value: '0%', detail: 'Waiting for live data' },
]

const navItems = [
  { id: 'overview', label: 'Overview' },
  { id: 'pgs', label: 'Properties' },
  { id: 'tenants', label: 'Tenants' },
  { id: 'spending', label: 'Spending' },
  { id: 'rooms', label: 'Rooms & Beds' },
  { id: 'finance', label: 'Rent & Payments' },
  { id: 'reports', label: 'Reports' },
] as const

const formatCurrency = (value: number) => `₹${new Intl.NumberFormat('en-IN').format(value)}`

const getDefaultRoomForm = (pgId = ''): RoomForm => ({
  pg_property_id: pgId,
  room_number: '',
  floor: 1,
  room_type: 'Shared',
  capacity: 2,
  monthly_rent: 5000,
  status: 'available',
  description: '',
})

const getDefaultTenantForm = (pgId = ''): TenantForm => ({
  pg_property_id: pgId,
  full_name: '',
  phone_number: '',
  email: '',
  date_of_birth: '',
  gender: 'Male',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  government_id_type: 'Aadhaar',
  government_id_number: '',
  joining_date: new Date().toISOString().slice(0, 10),
  expected_leaving_date: '',
  actual_leaving_date: '',
  deposit_amount: 0,
  status: 'active',
})

const getDefaultBedForm = (roomId = ''): {
  room_id: string
  bed_number: string
  status: string
} => ({
  room_id: roomId,
  bed_number: '',
  status: 'available',
})

const getDefaultAllocationForm = (pgId = '', tenantId = '', bedId = ''): {
  tenant_id: string
  bed_id: string
  pg_property_id: string
  start_date: string
  end_date: string
  notes: string
} => ({
  tenant_id: tenantId,
  bed_id: bedId,
  pg_property_id: pgId,
  start_date: new Date().toISOString().slice(0, 10),
  end_date: '',
  notes: '',
})

const getDefaultRentRecordForm = (pgId = '', tenantId = ''): {
  tenant_id: string
  pg_property_id: string
  month: string
  amount: number
  due_date: string
  notes: string
} => ({
  tenant_id: tenantId,
  pg_property_id: pgId,
  month: new Date().toISOString().slice(0, 7),
  amount: 0,
  due_date: new Date().toISOString().slice(0, 10),
  notes: '',
})

const getDefaultPaymentForm = (pgId = '', tenantId = ''): {
  tenant_id: string
  pg_property_id: string
  rent_record_id: string
  amount: number
  payment_date: string
  payment_mode: string
  reference_number: string
  notes: string
} => ({
  tenant_id: tenantId,
  pg_property_id: pgId,
  rent_record_id: '',
  amount: 0,
  payment_date: new Date().toISOString().slice(0, 10),
  payment_mode: 'UPI',
  reference_number: '',
  notes: '',
})

const getDefaultDepositForm = (pgId = '', tenantId = ''): {
  tenant_id: string
  pg_property_id: string
  amount: number
  deposit_date: string
  payment_mode: string
  reference_number: string
  notes: string
} => ({
  tenant_id: tenantId,
  pg_property_id: pgId,
  amount: 0,
  deposit_date: new Date().toISOString().slice(0, 10),
  payment_mode: 'UPI',
  reference_number: '',
  notes: '',
})

const getDefaultExpenseForm = (pgId = ''): {
  pg_property_id: string
  category: string
  description: string
  amount: number
  expense_date: string
  vendor: string
  payment_mode: string
  reference_number: string
  notes: string
} => ({
  pg_property_id: pgId,
  category: 'Utilities',
  description: '',
  amount: 0,
  expense_date: new Date().toISOString().slice(0, 10),
  vendor: '',
  payment_mode: 'UPI',
  reference_number: '',
  notes: '',
})

function getStoredToken() {
  return localStorage.getItem('pg_portal_role') ? 'portal' : null
}

function App() {
  useEffect(() => {
    localStorage.removeItem('pg_token')
  }, [])

  const [portalRole, setPortalRole] = useState<'OWNER' | 'TENANT' | null>(() => {
    const storedRole = localStorage.getItem('pg_portal_role')
    return storedRole === 'OWNER' || storedRole === 'TENANT' ? storedRole : null
  })
  const user: User | null = portalRole
    ? {
        id: `portal-${portalRole.toLowerCase()}`,
        username: portalRole.toLowerCase(),
        email: '',
        full_name: portalRole === 'OWNER' ? 'Owner' : 'Tenant',
        role: portalRole,
      }
    : null

  const handlePortalSelect = (role: 'OWNER' | 'TENANT') => {
    localStorage.removeItem('pg_token')
    localStorage.setItem('pg_portal_role', role)
    setPortalRole(role)
  }

  const handleLogout = () => {
    localStorage.removeItem('pg_token')
    localStorage.removeItem('pg_portal_role')
    setPortalRole(null)
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            user ? (
              <Navigate to={user.role === 'TENANT' ? '/tenant-dashboard' : '/dashboard'} replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/login"
          element={
            user ? (
              <Navigate to={user.role === 'TENANT' ? '/tenant-dashboard' : '/dashboard'} replace />
            ) : (
              <LoginPage onSelectPortal={handlePortalSelect} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            user ? (
              user.role === 'TENANT' ? (
                <Navigate to="/tenant-dashboard" replace />
              ) : (
                <DashboardPage onLogout={handleLogout} />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/tenant-dashboard"
          element={
            user ? (
              user.role === 'TENANT' ? (
                <TenantDashboard onLogout={handleLogout} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

function LoginPage({ onSelectPortal }: { onSelectPortal: (role: 'OWNER' | 'TENANT') => void }) {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="brand-block">
          <span className="brand-tag">PG MANAGEMENT</span>
          <h1>Choose your portal</h1>
        </div>

        <div className="login-actions">
          <button className="primary-button" type="button" onClick={() => onSelectPortal('OWNER')}>
            Owner
          </button>
          <button className="secondary-button" type="button" onClick={() => onSelectPortal('TENANT')}>
            Tenant
          </button>
        </div>
      </div>
    </div>
  )
}

function TenantDashboard({ onLogout }: { onLogout: () => void }) {
  const [tenantId, setTenantId] = useState('')
  const [tenantDetails, setTenantDetails] = useState<TenantDetailsRecord | null>(null)
  const [lookupError, setLookupError] = useState('')
  const [lookupLoading, setLookupLoading] = useState(false)

  const handleTenantLookup = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLookupLoading(true)
    setLookupError('')
    setTenantDetails(null)

    try {
      const response = await api.get<TenantDetailsRecord>(`/tenants/${encodeURIComponent(tenantId.trim())}`)
      setTenantDetails(response.data)
    } catch (error) {
      setLookupError(axios.isAxiosError(error)
        ? error.response?.data?.detail || 'No tenant was found for that ID.'
        : 'Unable to look up tenant details.')
    } finally {
      setLookupLoading(false)
    }
  }

  return (
    <div className="app-shell dashboard-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">Tenant Portal</div>
        <nav className="nav">
          <button type="button" className="nav-item active">Tenant details</button>
        </nav>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Tenant portal</p>
            <h2>Find your details</h2>
          </div>
          <button className="secondary-button" onClick={onLogout} type="button">
            Back
          </button>
        </header>

        <section className="panel tenant-lookup-panel">
          <form className="tenant-lookup-form" onSubmit={handleTenantLookup}>
            <label>
              Tenant ID
              <input
                value={tenantId}
                onChange={(event) => setTenantId(event.target.value)}
                placeholder="Paste the unique tenant ID"
                required
              />
            </label>
            <button className="primary-button" type="submit" disabled={lookupLoading}>
              {lookupLoading ? 'Searching...' : 'Find tenant'}
            </button>
          </form>

          {lookupError ? <div className="error-box">{lookupError}</div> : null}
          {tenantDetails ? (
            <>
              <div className="panel-header tenant-result-header">
                <h3>{tenantDetails.full_name}</h3>
                <span>{tenantDetails.status}</span>
              </div>
              <dl className="tenant-details-grid">
                <div><dt>Tenant ID</dt><dd>{tenantDetails.id}</dd></div>
                <div><dt>PG</dt><dd>{tenantDetails.pg_property_name}</dd></div>
                <div><dt>Phone</dt><dd>{tenantDetails.phone_number}</dd></div>
                <div><dt>Email</dt><dd>{tenantDetails.email || 'Not provided'}</dd></div>
                <div><dt>Date of birth</dt><dd>{tenantDetails.date_of_birth || 'Not provided'}</dd></div>
                <div><dt>Gender</dt><dd>{tenantDetails.gender || 'Not provided'}</dd></div>
                <div><dt>Address</dt><dd>{tenantDetails.address || 'Not provided'}</dd></div>
                <div><dt>Emergency contact</dt><dd>{tenantDetails.emergency_contact || 'Not provided'}</dd></div>
                <div><dt>Emergency phone</dt><dd>{tenantDetails.emergency_phone || 'Not provided'}</dd></div>
                <div><dt>Government ID type</dt><dd>{tenantDetails.government_id_type || 'Not provided'}</dd></div>
                <div><dt>Government ID number</dt><dd>{tenantDetails.government_id_number || 'Not provided'}</dd></div>
                <div><dt>Joining date</dt><dd>{tenantDetails.joining_date}</dd></div>
                <div><dt>Expected leaving date</dt><dd>{tenantDetails.expected_leaving_date || 'Not set'}</dd></div>
                <div><dt>Actual leaving date</dt><dd>{tenantDetails.actual_leaving_date || 'Not set'}</dd></div>
                <div><dt>Deposit</dt><dd>{formatCurrency(tenantDetails.deposit_amount)}</dd></div>
                <div><dt>Active</dt><dd>{tenantDetails.is_active ? 'Yes' : 'No'}</dd></div>
              </dl>
            </>
          ) : null}
        </section>
      </main>
    </div>
  )
}

function DashboardPage({ onLogout }: { onLogout: () => void }) {
  const [statCards, setStatCards] = useState(defaultStatCards)
  const [occupancyRows, setOccupancyRows] = useState<OccupancyRow[]>([])
  const [loadingOverview, setLoadingOverview] = useState(true)
  const [activeNav, setActiveNav] = useState('overview')
  const [pgs, setPgs] = useState<PGRecord[]>([])
  const [rooms, setRooms] = useState<RoomRecord[]>([])
  const [tenants, setTenants] = useState<TenantRecord[]>([])
  const [beds, setBeds] = useState<BedRecord[]>([])
  const [allocations, setAllocations] = useState<AllocationRecord[]>([])
  const [rentRecords, setRentRecords] = useState<RentRecord[]>([])
  const [payments, setPayments] = useState<PaymentRecord[]>([])
  const [deposits, setDeposits] = useState<DepositRecord[]>([])
  const [expenses, setExpenses] = useState<ExpenseRecord[]>([])
  const [pgForm, setPgForm] = useState<PGForm>({
    name: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    contact_number: '',
    email: '',
    number_of_floors: 1,
    description: '',
    facilities: 'Wi-Fi, Laundry',
  })
  const [roomForm, setRoomForm] = useState<RoomForm>(getDefaultRoomForm())
  const [tenantForm, setTenantForm] = useState<TenantForm>(getDefaultTenantForm())
  const [bedForm, setBedForm] = useState(getDefaultBedForm())
  const [allocationForm, setAllocationForm] = useState(getDefaultAllocationForm())
  const [rentRecordForm, setRentRecordForm] = useState(getDefaultRentRecordForm())
  const [paymentForm, setPaymentForm] = useState(getDefaultPaymentForm())
  const [depositForm, setDepositForm] = useState(getDefaultDepositForm())
  const [expenseForm, setExpenseForm] = useState(getDefaultExpenseForm())
  const [pgSubmitting, setPgSubmitting] = useState(false)
  const [roomSubmitting, setRoomSubmitting] = useState(false)
  const [tenantSubmitting, setTenantSubmitting] = useState(false)
  const [bedSubmitting, setBedSubmitting] = useState(false)
  const [allocationSubmitting, setAllocationSubmitting] = useState(false)
  const [rentRecordSubmitting, setRentRecordSubmitting] = useState(false)
  const [paymentSubmitting, setPaymentSubmitting] = useState(false)
  const [depositSubmitting, setDepositSubmitting] = useState(false)
  const [expenseSubmitting, setExpenseSubmitting] = useState(false)
  const [pgMessage, setPgMessage] = useState('')
  const [roomMessage, setRoomMessage] = useState('')
  const [tenantMessage, setTenantMessage] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [bedMessage, setBedMessage] = useState('')
  const [allocationMessage, setAllocationMessage] = useState('')
  const [rentRecordMessage, setRentRecordMessage] = useState('')
  const [paymentMessage, setPaymentMessage] = useState('')
  const [depositMessage, setDepositMessage] = useState('')
  const [expenseMessage, setExpenseMessage] = useState('')

  const handleNavClick = (id: string) => {
    setActiveNav(id)
    const section = document.getElementById(id)
    if (section) {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const loadOverview = async () => {
    const token = getStoredToken()
    if (!token) {
      setLoadingOverview(false)
      return
    }

    try {
      const [pgsResponse, roomsResponse, tenantsResponse, bedsResponse, allocationsResponse, rentRecordsResponse, paymentsResponse, depositsResponse, expensesResponse] = await Promise.all([
        api.get<PGRecord[]>('/pgs', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<RoomRecord[]>('/rooms', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<TenantRecord[]>('/tenants', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<BedRecord[]>('/beds', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<AllocationRecord[]>('/allocations', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<RentRecord[]>('/rent-records', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<PaymentRecord[]>('/payments', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<DepositRecord[]>('/deposits', { headers: { Authorization: `Bearer ${token}` } }),
        api.get<ExpenseRecord[]>('/expenses', { headers: { Authorization: `Bearer ${token}` } }),
      ])

      const fetchedPgs = pgsResponse.data ?? []
      const fetchedRooms = roomsResponse.data ?? []
      const fetchedTenants = tenantsResponse.data ?? []
      const fetchedBeds = bedsResponse.data ?? []
      const fetchedAllocations = allocationsResponse.data ?? []
      const fetchedRentRecords = rentRecordsResponse.data ?? []
      const fetchedPayments = paymentsResponse.data ?? []
      const fetchedDeposits = depositsResponse.data ?? []
      const fetchedExpenses = expensesResponse.data ?? []
      setPgs(fetchedPgs)
      setRooms(fetchedRooms)
      setTenants(fetchedTenants)
      setBeds(fetchedBeds)
      setAllocations(fetchedAllocations)
      setRentRecords(fetchedRentRecords)
      setPayments(fetchedPayments)
      setDeposits(fetchedDeposits)
      setExpenses(fetchedExpenses)

      if (fetchedPgs.length > 0) {
        setRoomForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
        }))
        setTenantForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
        }))
        setBedForm((current) => ({
          ...current,
          room_id: current.room_id || fetchedRooms[0]?.id || '',
        }))
        setAllocationForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
          tenant_id: current.tenant_id || fetchedTenants[0]?.id || '',
          bed_id: current.bed_id || fetchedBeds[0]?.id || '',
        }))
        setRentRecordForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
          tenant_id: current.tenant_id || fetchedTenants[0]?.id || '',
        }))
        setPaymentForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
          tenant_id: current.tenant_id || fetchedTenants[0]?.id || '',
        }))
        setDepositForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
          tenant_id: current.tenant_id || fetchedTenants[0]?.id || '',
        }))
        setExpenseForm((current) => ({
          ...current,
          pg_property_id: current.pg_property_id || fetchedPgs[0].id,
        }))
      }

      const totalCapacity = fetchedRooms.reduce((sum, room) => sum + (room.capacity || 0), 0)
      const occupiedBeds = fetchedTenants.length
      const occupancyPercent = totalCapacity > 0 ? Math.min(100, Math.round((occupiedBeds / totalCapacity) * 100)) : 0

      const groupedOccupancy = fetchedPgs.map((pg) => {
        const pgRooms = fetchedRooms.filter((room) => room.pg_property_id === pg.id)
        const pgTenants = fetchedTenants.filter((tenant) => tenant.pg_property_id === pg.id).length
        const occupied = Math.min(pgRooms.length, pgTenants)
        const roomsCount = pgRooms.length
        const vacancy = Math.max(roomsCount - occupied, 0)

        return {
          name: pg.name,
          rooms: roomsCount,
          occupied,
          vacancy,
        }
      })

      setStatCards([
        { label: 'PGs', value: String(fetchedPgs.length), detail: fetchedPgs.length ? 'Active properties' : 'No properties yet' },
        { label: 'Rooms', value: String(fetchedRooms.length), detail: fetchedRooms.length ? 'Live room inventory' : 'No room inventory yet' },
        { label: 'Tenants', value: String(fetchedTenants.length), detail: fetchedTenants.length ? 'Occupied in active records' : 'No active tenants yet' },
        { label: 'Occupancy', value: `${occupancyPercent}%`, detail: `${occupiedBeds} tenants across ${totalCapacity} beds` },
      ])
      setOccupancyRows(groupedOccupancy)
    } catch {
      setPgs([])
      setRooms([])
      setTenants([])
      setBeds([])
      setAllocations([])
      setRentRecords([])
      setPayments([])
      setDeposits([])
      setExpenses([])
      setStatCards(defaultStatCards)
      setOccupancyRows([])
    } finally {
      setLoadingOverview(false)
    }
  }

  useEffect(() => {
    void loadOverview()
  }, [])

  const totalCollections = payments.reduce((sum, payment) => sum + Number(payment.amount || 0), 0)
  const totalDeposits = deposits.reduce((sum, deposit) => sum + Number(deposit.amount || 0), 0)
  const totalExpenses = expenses.reduce((sum, expense) => sum + Number(expense.amount || 0), 0)
  const netCashFlow = totalCollections + totalDeposits - totalExpenses

  const recentPayments = [...payments]
    .sort((left, right) => new Date(right.payment_date).valueOf() - new Date(left.payment_date).valueOf())
    .slice(0, 3)
    .map((payment) => {
      const tenant = tenants.find((item) => item.id === payment.tenant_id)
      return {
        tenant: tenant?.full_name || 'Tenant',
        amount: formatCurrency(Number(payment.amount || 0)),
        status: payment.status === 'paid' ? 'Paid' : 'Recorded',
      }
    })

  const handleCreatePG = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setPgMessage('You must be signed in to create a PG.')
      return
    }

    try {
      setPgSubmitting(true)
      setPgMessage('')
      const payload = {
        ...pgForm,
        number_of_floors: Number(pgForm.number_of_floors),
        facilities: pgForm.facilities
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
      }

      const response = await api.post<PGRecord>('/pgs', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setPgs((current) => [response.data, ...current])
      setPgForm({
        name: '',
        address: '',
        city: '',
        state: '',
        pincode: '',
        contact_number: '',
        email: '',
        number_of_floors: 1,
        description: '',
        facilities: 'Wi-Fi, Laundry',
      })
      setPgMessage('PG created successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to create PG.'
        : 'Unable to create PG.'
      setPgMessage(message)
    } finally {
      setPgSubmitting(false)
    }
  }

  const handleDeletePG = async (pg: PGRecord) => {
    const confirmed = window.confirm(
      `Delete ${pg.name}? Its rooms, tenants, and linked financial records will also be deleted.`,
    )
    if (!confirmed) return

    try {
      setDeletingId(pg.id)
      setPgMessage('')
      await api.delete(`/pgs/${pg.id}`)
      setPgMessage(`${pg.name} and its linked records were deleted.`)
      await loadOverview()
    } catch (err) {
      setPgMessage(axios.isAxiosError(err) ? err.response?.data?.detail || 'Unable to delete PG.' : 'Unable to delete PG.')
    } finally {
      setDeletingId(null)
    }
  }

  const handleCreateRoom = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setRoomMessage('You must be signed in to create a room.')
      return
    }
    if (!pgs.length) {
      setRoomMessage('Create a PG before adding a room.')
      return
    }

    try {
      setRoomSubmitting(true)
      setRoomMessage('')
      const payload = {
        ...roomForm,
        pg_property_id: roomForm.pg_property_id || pgs[0]?.id,
        floor: Number(roomForm.floor),
        capacity: Number(roomForm.capacity),
        monthly_rent: Number(roomForm.monthly_rent),
      }

      const response = await api.post<RoomRecord>('/rooms', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setRooms((current) => [response.data, ...current])
      setRoomForm((current) => ({
        ...getDefaultRoomForm(current.pg_property_id || pgs[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
      }))
      setRoomMessage('Room created successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to create room.'
        : 'Unable to create room.'
      setRoomMessage(message)
    } finally {
      setRoomSubmitting(false)
    }
  }

  const handleCreateTenant = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setTenantMessage('You must be signed in to create a tenant.')
      return
    }
    if (!pgs.length) {
      setTenantMessage('Create a PG before adding a tenant.')
      return
    }

    try {
      setTenantSubmitting(true)
      setTenantMessage('')

      const payload = {
        ...tenantForm,
        pg_property_id: tenantForm.pg_property_id || pgs[0]?.id,
        deposit_amount: Number(tenantForm.deposit_amount),
        email: tenantForm.email || null,
        date_of_birth: tenantForm.date_of_birth || null,
        expected_leaving_date: tenantForm.expected_leaving_date || null,
        actual_leaving_date: tenantForm.actual_leaving_date || null,
        address: tenantForm.address || null,
        emergency_contact: tenantForm.emergency_contact || null,
        emergency_phone: tenantForm.emergency_phone || null,
        government_id_type: tenantForm.government_id_type || null,
        government_id_number: tenantForm.government_id_number || null,
      }

      const response = await api.post<TenantRecord>('/tenants', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setTenants((current) => [response.data, ...current])
      setTenantForm((current) => ({
        ...getDefaultTenantForm(current.pg_property_id || pgs[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
      }))
      setTenantMessage('Tenant created successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to create tenant.'
        : 'Unable to create tenant.'
      setTenantMessage(message)
    } finally {
      setTenantSubmitting(false)
    }
  }

  const handleDeleteTenant = async (tenant: TenantRecord) => {
    const confirmed = window.confirm(
      `Delete ${tenant.full_name}? Their allocation, rent, payment, and deposit records will also be deleted.`,
    )
    if (!confirmed) return

    try {
      setDeletingId(tenant.id)
      setTenantMessage('')
      await api.delete(`/tenants/${tenant.id}`)
      setTenantMessage(`${tenant.full_name} and their linked records were deleted.`)
      await loadOverview()
    } catch (err) {
      setTenantMessage(axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to delete tenant.'
        : 'Unable to delete tenant.')
    } finally {
      setDeletingId(null)
    }
  }

  const handleCreateBed = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setBedMessage('You must be signed in to create a bed.')
      return
    }
    if (!rooms.length) {
      setBedMessage('Create a room before adding a bed.')
      return
    }

    try {
      setBedSubmitting(true)
      setBedMessage('')
      const payload = {
        ...bedForm,
        room_id: bedForm.room_id || rooms[0]?.id,
      }

      const response = await api.post<BedRecord>('/beds', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setBeds((current) => [response.data, ...current])
      setBedForm((current) => ({
        ...getDefaultBedForm(current.room_id || rooms[0]?.id || ''),
        room_id: current.room_id || rooms[0]?.id || '',
      }))
      setBedMessage('Bed created successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to create bed.'
        : 'Unable to create bed.'
      setBedMessage(message)
    } finally {
      setBedSubmitting(false)
    }
  }

  const handleCreateAllocation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setAllocationMessage('You must be signed in to assign a bed.')
      return
    }
    if (!tenants.length || !beds.length) {
      setAllocationMessage('Create a tenant and a bed before assigning a room.')
      return
    }

    try {
      setAllocationSubmitting(true)
      setAllocationMessage('')
      const payload = {
        ...allocationForm,
        tenant_id: allocationForm.tenant_id || tenants[0]?.id,
        bed_id: allocationForm.bed_id || beds[0]?.id,
        pg_property_id: allocationForm.pg_property_id || pgs[0]?.id,
        end_date: allocationForm.end_date || null,
      }

      const response = await api.post<AllocationRecord>('/allocations', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setAllocations((current) => [response.data, ...current])
      setAllocationForm((current) => ({
        ...getDefaultAllocationForm(current.pg_property_id || pgs[0]?.id || '', current.tenant_id || tenants[0]?.id || '', current.bed_id || beds[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
        tenant_id: current.tenant_id || tenants[0]?.id || '',
        bed_id: current.bed_id || beds[0]?.id || '',
      }))
      setAllocationMessage('Bed allocated successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to assign the bed.'
        : 'Unable to assign the bed.'
      setAllocationMessage(message)
    } finally {
      setAllocationSubmitting(false)
    }
  }

  const handleCreateRentRecord = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setRentRecordMessage('You must be signed in to create a rent record.')
      return
    }
    if (!tenants.length) {
      setRentRecordMessage('Create a tenant before creating a rent record.')
      return
    }

    try {
      setRentRecordSubmitting(true)
      setRentRecordMessage('')
      const payload = {
        ...rentRecordForm,
        tenant_id: rentRecordForm.tenant_id || tenants[0]?.id,
        pg_property_id: rentRecordForm.pg_property_id || pgs[0]?.id,
        amount: Number(rentRecordForm.amount),
      }

      const response = await api.post<RentRecord>('/rent-records', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setRentRecords((current) => [response.data, ...current])
      setRentRecordForm((current) => ({
        ...getDefaultRentRecordForm(current.pg_property_id || pgs[0]?.id || '', current.tenant_id || tenants[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
        tenant_id: current.tenant_id || tenants[0]?.id || '',
      }))
      setRentRecordMessage('Rent record created successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to create rent record.'
        : 'Unable to create rent record.'
      setRentRecordMessage(message)
    } finally {
      setRentRecordSubmitting(false)
    }
  }

  const handleCreatePayment = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setPaymentMessage('You must be signed in to create a payment.')
      return
    }
    if (!tenants.length) {
      setPaymentMessage('Create a tenant before recording a payment.')
      return
    }

    try {
      setPaymentSubmitting(true)
      setPaymentMessage('')
      const payload = {
        ...paymentForm,
        tenant_id: paymentForm.tenant_id || tenants[0]?.id,
        pg_property_id: paymentForm.pg_property_id || pgs[0]?.id,
        amount: Number(paymentForm.amount),
        rent_record_id: paymentForm.rent_record_id || null,
      }

      const response = await api.post<PaymentRecord>('/payments', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setPayments((current) => [response.data, ...current])
      setPaymentForm((current) => ({
        ...getDefaultPaymentForm(current.pg_property_id || pgs[0]?.id || '', current.tenant_id || tenants[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
        tenant_id: current.tenant_id || tenants[0]?.id || '',
      }))
      setPaymentMessage('Payment recorded successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to record payment.'
        : 'Unable to record payment.'
      setPaymentMessage(message)
    } finally {
      setPaymentSubmitting(false)
    }
  }

  const handleCreateDeposit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setDepositMessage('You must be signed in to create a deposit.')
      return
    }
    if (!tenants.length) {
      setDepositMessage('Create a tenant before recording a deposit.')
      return
    }

    try {
      setDepositSubmitting(true)
      setDepositMessage('')
      const payload = {
        ...depositForm,
        tenant_id: depositForm.tenant_id || tenants[0]?.id,
        pg_property_id: depositForm.pg_property_id || pgs[0]?.id,
        amount: Number(depositForm.amount),
      }

      const response = await api.post<DepositRecord>('/deposits', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setDeposits((current) => [response.data, ...current])
      setDepositForm((current) => ({
        ...getDefaultDepositForm(current.pg_property_id || pgs[0]?.id || '', current.tenant_id || tenants[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
        tenant_id: current.tenant_id || tenants[0]?.id || '',
      }))
      setDepositMessage('Deposit recorded successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to record deposit.'
        : 'Unable to record deposit.'
      setDepositMessage(message)
    } finally {
      setDepositSubmitting(false)
    }
  }

  const handleCreateExpense = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const token = getStoredToken()
    if (!token) {
      setExpenseMessage('You must be signed in to create an expense.')
      return
    }
    if (!pgs.length) {
      setExpenseMessage('Create a PG before recording an expense.')
      return
    }

    try {
      setExpenseSubmitting(true)
      setExpenseMessage('')
      const payload = {
        ...expenseForm,
        pg_property_id: expenseForm.pg_property_id || pgs[0]?.id,
        amount: Number(expenseForm.amount),
      }

      const response = await api.post<ExpenseRecord>('/expenses', payload, {
        headers: { Authorization: `Bearer ${token}` },
      })
      setExpenses((current) => [response.data, ...current])
      setExpenseForm((current) => ({
        ...getDefaultExpenseForm(current.pg_property_id || pgs[0]?.id || ''),
        pg_property_id: current.pg_property_id || pgs[0]?.id || '',
      }))
      setExpenseMessage('Expense recorded successfully.')
      await loadOverview()
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || 'Unable to record expense.'
        : 'Unable to record expense.'
      setExpenseMessage(message)
    } finally {
      setExpenseSubmitting(false)
    }
  }

  return (
    <div className="app-shell dashboard-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">PG Hub</div>
        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Owner workspace</p>
            <h2>Property overview</h2>
          </div>
          <button className="secondary-button" onClick={onLogout} type="button">
            Logout
          </button>
        </header>

        <section id="overview" className="stats-grid">
          {statCards.map((card) => (
            <article className="stat-card" key={card.label}>
              <p>{card.label}</p>
              <h3>{card.value}</h3>
              <span>{card.detail}</span>
            </article>
          ))}
        </section>

        <section className="panel-grid">
          <article className="panel">
            <div className="panel-header">
              <h3>Occupancy</h3>
              <span>{loadingOverview ? 'Syncing...' : 'Live'}</span>
            </div>
            <div className="table">
              {occupancyRows.map((row) => (
                <div className="table-row" key={row.name}>
                  <div>
                    <strong>{row.name}</strong>
                  </div>
                  <div>{row.occupied}/{row.rooms}</div>
                  <div>{row.vacancy} vacant</div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h3>Recent payments</h3>
              <span>{recentPayments.length ? 'Live' : 'Today'}</span>
            </div>
            <div className="table compact">
              {recentPayments.length ? (
                recentPayments.map((row) => (
                  <div className="table-row" key={`${row.tenant}-${row.amount}`}>
                    <div>
                      <strong>{row.tenant}</strong>
                    </div>
                    <div>{row.amount}</div>
                    <div className={row.status === 'Paid' ? 'badge success' : 'badge warning'}>
                      {row.status}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No payment activity yet.</div>
              )}
            </div>
          </article>
        </section>

        <section className="management-grid">
          <article className="panel">
            <div className="panel-header">
              <h3>Bed inventory</h3>
              <span>{beds.length} total</span>
            </div>
            <div className="table compact">
              {beds.length ? (
                beds.slice(0, 6).map((bed) => (
                  <div className="table-row" key={bed.id}>
                    <div>
                      <strong>{bed.bed_number}</strong>
                    </div>
                    <div>{bed.status}</div>
                    <div>{allocations.some((allocation) => allocation.bed_id === bed.id && allocation.is_active) ? 'Assigned' : 'Open'}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No beds created yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateBed}>
              <div className="field-grid">
                <label>
                  Room
                  <select
                    value={bedForm.room_id}
                    onChange={(event) => setBedForm((current) => ({ ...current, room_id: event.target.value }))}
                  >
                    {rooms.map((room) => (
                      <option key={room.id} value={room.id}>
                        {room.room_number}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Bed number
                  <input
                    value={bedForm.bed_number}
                    onChange={(event) => setBedForm((current) => ({ ...current, bed_number: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Status
                  <select
                    value={bedForm.status}
                    onChange={(event) => setBedForm((current) => ({ ...current, status: event.target.value }))}
                  >
                    <option value="available">Available</option>
                    <option value="occupied">Occupied</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                </label>
              </div>

              {bedMessage ? <div className="form-message">{bedMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={bedSubmitting}>
                {bedSubmitting ? 'Creating...' : 'Create Bed'}
              </button>
            </form>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h3>Bed allocation</h3>
              <span>{allocations.length} active</span>
            </div>
            <div className="table compact">
              {allocations.length ? (
                allocations.slice(0, 6).map((allocation) => (
                  <div className="table-row" key={allocation.id}>
                    <div>
                      <strong>{tenants.find((tenant) => tenant.id === allocation.tenant_id)?.full_name || 'Tenant'}</strong>
                    </div>
                    <div>{beds.find((bed) => bed.id === allocation.bed_id)?.bed_number || 'Bed'}</div>
                    <div>{allocation.status}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No active allocations yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateAllocation}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={allocationForm.pg_property_id}
                    onChange={(event) =>
                      setAllocationForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>{pg.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Tenant
                  <select
                    value={allocationForm.tenant_id}
                    onChange={(event) =>
                      setAllocationForm((current) => ({ ...current, tenant_id: event.target.value }))
                    }
                  >
                    {tenants.map((tenant) => (
                      <option key={tenant.id} value={tenant.id}>{tenant.full_name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Bed
                  <select
                    value={allocationForm.bed_id}
                    onChange={(event) =>
                      setAllocationForm((current) => ({ ...current, bed_id: event.target.value }))
                    }
                  >
                    {beds.map((bed) => (
                      <option key={bed.id} value={bed.id}>{bed.bed_number}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Start date
                  <input
                    type="date"
                    value={allocationForm.start_date}
                    onChange={(event) =>
                      setAllocationForm((current) => ({ ...current, start_date: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  End date
                  <input
                    type="date"
                    value={allocationForm.end_date}
                    onChange={(event) =>
                      setAllocationForm((current) => ({ ...current, end_date: event.target.value }))
                    }
                  />
                </label>
                <label className="full-width">
                  Notes
                  <textarea
                    value={allocationForm.notes}
                    onChange={(event) =>
                      setAllocationForm((current) => ({ ...current, notes: event.target.value }))
                    }
                    rows={2}
                  />
                </label>
              </div>

              {allocationMessage ? <div className="form-message">{allocationMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={allocationSubmitting}>
                {allocationSubmitting ? 'Assigning...' : 'Assign Bed'}
              </button>
            </form>
          </article>
        </section>

        <section id="reports" className="report-grid">
          <article className="report-card">
            <span>Collections</span>
            <strong>{formatCurrency(totalCollections)}</strong>
            <small>Payments received</small>
          </article>
          <article className="report-card">
            <span>Deposits</span>
            <strong>{formatCurrency(totalDeposits)}</strong>
            <small>Security deposits</small>
          </article>
          <article className="report-card">
            <span>Expenses</span>
            <strong>{formatCurrency(totalExpenses)}</strong>
            <small>Operating costs</small>
          </article>
          <article className="report-card highlight">
            <span>Net cash flow</span>
            <strong>{formatCurrency(netCashFlow)}</strong>
            <small>Collections minus expenses</small>
          </article>
        </section>

        <section id="finance" className="finance-grid rent-grid">
          <article className="panel">
            <div className="panel-header">
              <h3>Rent ledger</h3>
              <span>{rentRecords.length} total</span>
            </div>
            <div className="table compact">
              {rentRecords.length ? (
                rentRecords.slice(0, 6).map((record) => (
                  <div className="table-row" key={record.id}>
                    <div>
                      <strong>{tenants.find((tenant) => tenant.id === record.tenant_id)?.full_name || 'Tenant'}</strong>
                    </div>
                    <div>{record.month}</div>
                    <div>{record.status}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No rent records created yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateRentRecord}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={rentRecordForm.pg_property_id}
                    onChange={(event) =>
                      setRentRecordForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>{pg.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Tenant
                  <select
                    value={rentRecordForm.tenant_id}
                    onChange={(event) =>
                      setRentRecordForm((current) => ({ ...current, tenant_id: event.target.value }))
                    }
                  >
                    {tenants.map((tenant) => (
                      <option key={tenant.id} value={tenant.id}>{tenant.full_name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Month
                  <input
                    type="month"
                    value={rentRecordForm.month}
                    onChange={(event) =>
                      setRentRecordForm((current) => ({ ...current, month: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Amount
                  <input
                    type="number"
                    min={0}
                    value={rentRecordForm.amount}
                    onChange={(event) =>
                      setRentRecordForm((current) => ({ ...current, amount: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label>
                  Due date
                  <input
                    type="date"
                    value={rentRecordForm.due_date}
                    onChange={(event) =>
                      setRentRecordForm((current) => ({ ...current, due_date: event.target.value }))
                    }
                    required
                  />
                </label>
                <label className="full-width">
                  Notes
                  <textarea
                    value={rentRecordForm.notes}
                    onChange={(event) =>
                      setRentRecordForm((current) => ({ ...current, notes: event.target.value }))
                    }
                    rows={2}
                  />
                </label>
              </div>

              {rentRecordMessage ? <div className="form-message">{rentRecordMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={rentRecordSubmitting}>
                {rentRecordSubmitting ? 'Creating...' : 'Create Rent Record'}
              </button>
            </form>
          </article>
        </section>

        <section id="pgs" className="management-grid">
          <article className="panel">
            <div className="panel-header">
              <h3>Your properties</h3>
              <span>{pgs.length} properties</span>
            </div>
            <p className="section-description">Add a PG first. Rooms, tenants, and spending are connected to a property.</p>
            <div className="pg-list">
              {pgs.length ? (
                pgs.map((pg) => (
                  <div className="pg-item" key={pg.id}>
                    <div className="pg-item-main">
                      <strong>{pg.name}</strong>
                      <small>
                        {pg.city} · {pg.address}
                      </small>
                    </div>
                    <div className="pg-item-actions">
                      <span>{pg.number_of_floors} floors</span>
                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => void handleDeletePG(pg)}
                        disabled={deletingId === pg.id}
                      >
                        {deletingId === pg.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No PGs created yet.</div>
              )}
            </div>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h3>Add a property</h3>
              <span>Property details</span>
            </div>
            <form className="pg-form" onSubmit={handleCreatePG}>
              <div className="field-grid">
                <label>
                  PG name
                  <input
                    value={pgForm.name}
                    onChange={(event) => setPgForm((current) => ({ ...current, name: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Email
                  <input
                    type="email"
                    value={pgForm.email}
                    onChange={(event) => setPgForm((current) => ({ ...current, email: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Address
                  <input
                    value={pgForm.address}
                    onChange={(event) => setPgForm((current) => ({ ...current, address: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  City
                  <input
                    value={pgForm.city}
                    onChange={(event) => setPgForm((current) => ({ ...current, city: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  State
                  <input
                    value={pgForm.state}
                    onChange={(event) => setPgForm((current) => ({ ...current, state: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Pincode
                  <input
                    value={pgForm.pincode}
                    onChange={(event) => setPgForm((current) => ({ ...current, pincode: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Contact
                  <input
                    value={pgForm.contact_number}
                    onChange={(event) => setPgForm((current) => ({ ...current, contact_number: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Floors
                  <input
                    type="number"
                    min={1}
                    value={pgForm.number_of_floors}
                    onChange={(event) =>
                      setPgForm((current) => ({ ...current, number_of_floors: Number(event.target.value) || 1 }))
                    }
                    required
                  />
                </label>
                <label className="full-width">
                  Facilities
                  <input
                    value={pgForm.facilities}
                    onChange={(event) => setPgForm((current) => ({ ...current, facilities: event.target.value }))}
                    placeholder="Wi-Fi, Laundry, Food"
                  />
                </label>
                <label className="full-width">
                  Description
                  <textarea
                    value={pgForm.description}
                    onChange={(event) => setPgForm((current) => ({ ...current, description: event.target.value }))}
                    rows={3}
                  />
                </label>
              </div>

              {pgMessage ? <div className="form-message">{pgMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={pgSubmitting}>
                {pgSubmitting ? 'Creating...' : 'Create PG'}
              </button>
            </form>
          </article>
        </section>

        <section id="rooms" className="operations-grid">
          <article className="panel">
            <div className="panel-header">
              <h3>Rooms</h3>
              <span>{rooms.length} total</span>
            </div>
            <div className="table compact">
              {rooms.length ? (
                rooms.map((room) => (
                  <div className="table-row" key={room.id}>
                    <div>
                      <strong>{room.room_number}</strong>
                    </div>
                    <div>{room.room_type}</div>
                    <div>{room.monthly_rent ? `₹${room.monthly_rent}` : '₹0'}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No rooms created yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateRoom}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={roomForm.pg_property_id}
                    onChange={(event) =>
                      setRoomForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>
                        {pg.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Room number
                  <input
                    value={roomForm.room_number}
                    onChange={(event) => setRoomForm((current) => ({ ...current, room_number: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Floor
                  <input
                    type="number"
                    min={0}
                    value={roomForm.floor}
                    onChange={(event) =>
                      setRoomForm((current) => ({ ...current, floor: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label>
                  Type
                  <select
                    value={roomForm.room_type}
                    onChange={(event) =>
                      setRoomForm((current) => ({ ...current, room_type: event.target.value }))
                    }
                  >
                    <option value="Shared">Shared</option>
                    <option value="Private">Private</option>
                    <option value="Studio">Studio</option>
                  </select>
                </label>
                <label>
                  Capacity
                  <input
                    type="number"
                    min={1}
                    value={roomForm.capacity}
                    onChange={(event) =>
                      setRoomForm((current) => ({ ...current, capacity: Number(event.target.value) || 1 }))
                    }
                    required
                  />
                </label>
                <label>
                  Monthly rent
                  <input
                    type="number"
                    min={0}
                    value={roomForm.monthly_rent}
                    onChange={(event) =>
                      setRoomForm((current) => ({ ...current, monthly_rent: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label className="full-width">
                  Description
                  <textarea
                    value={roomForm.description}
                    onChange={(event) => setRoomForm((current) => ({ ...current, description: event.target.value }))}
                    rows={2}
                  />
                </label>
              </div>

              {roomMessage ? <div className="form-message">{roomMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={roomSubmitting}>
                {roomSubmitting ? 'Creating...' : 'Create Room'}
              </button>
            </form>
          </article>

          <article id="tenants" className="panel tenant-management-panel">
            <div className="panel-header">
              <h3>Tenant register</h3>
              <span>{tenants.length} tenants</span>
            </div>
            <p className="section-description">Choose a property, add the tenant’s details, then share their generated Tenant ID.</p>
            <div className="table compact">
              {tenants.length ? (
                tenants.map((tenant) => (
                  <div className="table-row tenant-list-row" key={tenant.id}>
                    <div>
                      <strong>{tenant.full_name}</strong>
                      <small className="tenant-id">Tenant ID: {tenant.id}</small>
                    </div>
                    <div>{tenant.status}</div>
                    <div>{tenant.deposit_amount ? `₹${tenant.deposit_amount}` : '₹0'}</div>
                    <button
                      type="button"
                      className="danger-button"
                      onClick={() => void handleDeleteTenant(tenant)}
                      disabled={deletingId === tenant.id}
                    >
                      {deletingId === tenant.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                ))
              ) : (
                <div className="empty-state">No tenants added yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateTenant}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={tenantForm.pg_property_id}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>
                        {pg.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Full name
                  <input
                    value={tenantForm.full_name}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, full_name: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Phone
                  <input
                    value={tenantForm.phone_number}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, phone_number: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Email
                  <input
                    type="email"
                    value={tenantForm.email}
                    onChange={(event) => setTenantForm((current) => ({ ...current, email: event.target.value }))}
                  />
                </label>
                <label>
                  DOB
                  <input
                    type="date"
                    value={tenantForm.date_of_birth}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, date_of_birth: event.target.value }))
                    }
                  />
                </label>
                <label>
                  Gender
                  <select
                    value={tenantForm.gender}
                    onChange={(event) => setTenantForm((current) => ({ ...current, gender: event.target.value }))}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </label>
                <label className="full-width">
                  Address
                  <textarea
                    value={tenantForm.address}
                    onChange={(event) => setTenantForm((current) => ({ ...current, address: event.target.value }))}
                    rows={2}
                  />
                </label>
                <label>
                  Emergency contact
                  <input
                    value={tenantForm.emergency_contact}
                    onChange={(event) => setTenantForm((current) => ({ ...current, emergency_contact: event.target.value }))}
                  />
                </label>
                <label>
                  Emergency phone
                  <input
                    value={tenantForm.emergency_phone}
                    onChange={(event) => setTenantForm((current) => ({ ...current, emergency_phone: event.target.value }))}
                  />
                </label>
                <label>
                  Government ID type
                  <input
                    value={tenantForm.government_id_type}
                    onChange={(event) => setTenantForm((current) => ({ ...current, government_id_type: event.target.value }))}
                  />
                </label>
                <label>
                  Government ID number
                  <input
                    value={tenantForm.government_id_number}
                    onChange={(event) => setTenantForm((current) => ({ ...current, government_id_number: event.target.value }))}
                  />
                </label>
                <label>
                  Join date
                  <input
                    type="date"
                    value={tenantForm.joining_date}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, joining_date: event.target.value }))}
                    required
                  />
                </label>
                <label>
                  Expected leave
                  <input
                    type="date"
                    value={tenantForm.expected_leaving_date}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, expected_leaving_date: event.target.value }))
                    }
                  />
                </label>
                <label>
                  Actual leave
                  <input
                    type="date"
                    value={tenantForm.actual_leaving_date}
                    onChange={(event) => setTenantForm((current) => ({ ...current, actual_leaving_date: event.target.value }))}
                  />
                </label>
                <label>
                  Deposit
                  <input
                    type="number"
                    min={0}
                    value={tenantForm.deposit_amount}
                    onChange={(event) =>
                      setTenantForm((current) => ({ ...current, deposit_amount: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label>
                  Status
                  <select
                    value={tenantForm.status}
                    onChange={(event) => setTenantForm((current) => ({ ...current, status: event.target.value }))}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="vacating">Vacating</option>
                  </select>
                </label>
              </div>

              {tenantMessage ? <div className="form-message">{tenantMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={tenantSubmitting}>
                {tenantSubmitting ? 'Adding...' : 'Add Tenant'}
              </button>
            </form>
          </article>
        </section>

        <section className="finance-grid">
          <article className="panel">
            <div className="panel-header">
              <h3>Payments</h3>
              <span>{payments.length} total</span>
            </div>
            <div className="table compact">
              {payments.length ? (
                payments.slice(0, 5).map((payment) => (
                  <div className="table-row" key={payment.id}>
                    <div>
                      <strong>{payment.reference_number || 'Payment'}</strong>
                    </div>
                    <div>{payment.payment_mode}</div>
                    <div>₹{payment.amount}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No payments recorded yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreatePayment}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={paymentForm.pg_property_id}
                    onChange={(event) =>
                      setPaymentForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>{pg.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Tenant
                  <select
                    value={paymentForm.tenant_id}
                    onChange={(event) =>
                      setPaymentForm((current) => ({ ...current, tenant_id: event.target.value }))
                    }
                  >
                    {tenants.map((tenant) => (
                      <option key={tenant.id} value={tenant.id}>{tenant.full_name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Amount
                  <input
                    type="number"
                    min={1}
                    value={paymentForm.amount}
                    onChange={(event) =>
                      setPaymentForm((current) => ({ ...current, amount: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label>
                  Payment date
                  <input
                    type="date"
                    value={paymentForm.payment_date}
                    onChange={(event) =>
                      setPaymentForm((current) => ({ ...current, payment_date: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Mode
                  <select
                    value={paymentForm.payment_mode}
                    onChange={(event) =>
                      setPaymentForm((current) => ({ ...current, payment_mode: event.target.value }))
                    }
                  >
                    <option value="UPI">UPI</option>
                    <option value="Cash">Cash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="Card">Card</option>
                  </select>
                </label>
                <label>
                  Reference
                  <input
                    value={paymentForm.reference_number}
                    onChange={(event) =>
                      setPaymentForm((current) => ({ ...current, reference_number: event.target.value }))
                    }
                  />
                </label>
                <label className="full-width">
                  Notes
                  <textarea
                    value={paymentForm.notes}
                    onChange={(event) => setPaymentForm((current) => ({ ...current, notes: event.target.value }))}
                    rows={2}
                  />
                </label>
              </div>

              {paymentMessage ? <div className="form-message">{paymentMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={paymentSubmitting}>
                {paymentSubmitting ? 'Recording...' : 'Record Payment'}
              </button>
            </form>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h3>Deposits</h3>
              <span>{deposits.length} total</span>
            </div>
            <div className="table compact">
              {deposits.length ? (
                deposits.slice(0, 5).map((deposit) => (
                  <div className="table-row" key={deposit.id}>
                    <div>
                      <strong>{deposit.reference_number || 'Deposit'}</strong>
                    </div>
                    <div>{deposit.payment_mode}</div>
                    <div>₹{deposit.amount}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No deposits recorded yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateDeposit}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={depositForm.pg_property_id}
                    onChange={(event) =>
                      setDepositForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>{pg.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Tenant
                  <select
                    value={depositForm.tenant_id}
                    onChange={(event) =>
                      setDepositForm((current) => ({ ...current, tenant_id: event.target.value }))
                    }
                  >
                    {tenants.map((tenant) => (
                      <option key={tenant.id} value={tenant.id}>{tenant.full_name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Amount
                  <input
                    type="number"
                    min={1}
                    value={depositForm.amount}
                    onChange={(event) =>
                      setDepositForm((current) => ({ ...current, amount: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label>
                  Deposit date
                  <input
                    type="date"
                    value={depositForm.deposit_date}
                    onChange={(event) =>
                      setDepositForm((current) => ({ ...current, deposit_date: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Mode
                  <select
                    value={depositForm.payment_mode}
                    onChange={(event) =>
                      setDepositForm((current) => ({ ...current, payment_mode: event.target.value }))
                    }
                  >
                    <option value="UPI">UPI</option>
                    <option value="Cash">Cash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="Card">Card</option>
                  </select>
                </label>
                <label>
                  Reference
                  <input
                    value={depositForm.reference_number}
                    onChange={(event) =>
                      setDepositForm((current) => ({ ...current, reference_number: event.target.value }))
                    }
                  />
                </label>
                <label className="full-width">
                  Notes
                  <textarea
                    value={depositForm.notes}
                    onChange={(event) => setDepositForm((current) => ({ ...current, notes: event.target.value }))}
                    rows={2}
                  />
                </label>
              </div>

              {depositMessage ? <div className="form-message">{depositMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={depositSubmitting}>
                {depositSubmitting ? 'Recording...' : 'Record Deposit'}
              </button>
            </form>
          </article>

          <article id="spending" className="panel">
            <div className="panel-header">
              <h3>Spending</h3>
              <span>{expenses.length} records</span>
            </div>
            <p className="section-description">Track operating costs and assign every expense to its PG.</p>
            <div className="table compact">
              {expenses.length ? (
                expenses.slice(0, 5).map((expense) => (
                  <div className="table-row" key={expense.id}>
                    <div>
                      <strong>{expense.category}</strong>
                    </div>
                    <div>{expense.vendor || 'Vendor'}</div>
                    <div>₹{expense.amount}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No expenses recorded yet.</div>
              )}
            </div>

            <form className="pg-form compact-form" onSubmit={handleCreateExpense}>
              <div className="field-grid">
                <label>
                  PG
                  <select
                    value={expenseForm.pg_property_id}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, pg_property_id: event.target.value }))
                    }
                  >
                    {pgs.map((pg) => (
                      <option key={pg.id} value={pg.id}>{pg.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Category
                  <select
                    value={expenseForm.category}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, category: event.target.value }))
                    }
                  >
                    <option value="Utilities">Utilities</option>
                    <option value="Maintenance">Maintenance</option>
                    <option value="Cleaning">Cleaning</option>
                    <option value="Food">Food</option>
                    <option value="Other">Other</option>
                  </select>
                </label>
                <label className="full-width">
                  Description
                  <textarea
                    value={expenseForm.description}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, description: event.target.value }))
                    }
                    rows={2}
                    required
                  />
                </label>
                <label>
                  Amount
                  <input
                    type="number"
                    min={1}
                    value={expenseForm.amount}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, amount: Number(event.target.value) || 0 }))
                    }
                    required
                  />
                </label>
                <label>
                  Expense date
                  <input
                    type="date"
                    value={expenseForm.expense_date}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, expense_date: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  Vendor
                  <input
                    value={expenseForm.vendor}
                    onChange={(event) => setExpenseForm((current) => ({ ...current, vendor: event.target.value }))}
                  />
                </label>
                <label>
                  Mode
                  <select
                    value={expenseForm.payment_mode}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, payment_mode: event.target.value }))
                    }
                  >
                    <option value="UPI">UPI</option>
                    <option value="Cash">Cash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="Card">Card</option>
                  </select>
                </label>
                <label>
                  Reference
                  <input
                    value={expenseForm.reference_number}
                    onChange={(event) =>
                      setExpenseForm((current) => ({ ...current, reference_number: event.target.value }))
                    }
                  />
                </label>
                <label className="full-width">
                  Notes
                  <textarea
                    value={expenseForm.notes}
                    onChange={(event) => setExpenseForm((current) => ({ ...current, notes: event.target.value }))}
                    rows={2}
                  />
                </label>
              </div>

              {expenseMessage ? <div className="form-message">{expenseMessage}</div> : null}

              <button type="submit" className="primary-button" disabled={expenseSubmitting}>
                {expenseSubmitting ? 'Recording...' : 'Record Expense'}
              </button>
            </form>
          </article>
        </section>
      </main>
    </div>
  )
}

export default App
