# 작업 지침

## 코드 변경 전
- 변경하려는 이유와 목적을 먼저 설명할 것
- 어떤 파일의 어떤 부분을 수정할지 명시할 것
- 예상되는 영향 범위 설명할 것
- **⚠️ 보안 영향 검토**: 아래 체크리스트 중 해당 항목 확인

---

## 보안 검토 체크리스트

### 모든 코드 작성 시 필수 확인
코드 작성 완료 전 해당되는 항목을 반드시 점검할 것.

## 1. 데이터 보안 및 암호화 (Data Protection)
- **민감 정보 보호**: PII(개인식별정보), API 키, DB 비밀번호 등이 로그나 소스 코드에 평문으로 노출되지 않는가?
- **전송 시 암호화**: 모든 데이터 전송에 HTTPS(TLS 1.2 이상)를 강제하는가?
- **Secrets 관리**: `.env`, `Vault`, `K8s Secrets` 등을 사용하여 환경 변수로 관리하고 있는가?

## 2. 입력값 검증 및 출력 인코딩 (Input/Output Security)
- **SQL Injection 방지**: ORM(Django ORM 등)을 사용하거나 Parameterized Query를 사용하여 직접적인 쿼리 조립을 피했는가?
- **XSS 방지**: 사용자 입력값을 렌더링할 때 적절한 이스케이프 처리를 수행하는가?
- **CSRF 방지**: 모든 상태 변경 요청(POST, PUT, DELETE 등)에 CSRF 토큰 검증이 포함되었는가?
- **경로 조작(Path Traversal)**: 사용자 입력값이 파일 경로 설정에 직접 사용되지 않도록 검증하는가?

## 3. 에러 핸들링 및 로깅 (Error Handling & Logging)
- **상세 에러 노출 금지**: 사용자에게 노출되는 에러 메시지에 Stack Trace나 DB 구조 등 시스템 내부 정보가 포함되지 않았는가?
- **보안 이벤트 로깅**: 로그인 실패, 권한 거부, 중요 데이터 변경 등에 대한 로그를 남기고 있는가?
- **로그 주입 방지**: 로그 기록 시 개행 문자나 특수 문자를 필터링하여 로그 위조를 방지하는가?

## 4. 인프라 및 컨테이너 보안 (Infrastructure & Docker/K8s)
- **Base Image 보안**: Dockerfile 작성 시 공식적이고 최소화된(slim, alpine 등) 이미지를 사용하는가?
- **Root 권한 제한**: 컨테이너가 Root 사용자로 실행되지 않도록 `USER` 지시어를 사용하는가?
- **K8s RBAC**: 서비스 어카운트에 과도한 권한이 부여되지 않았는가?
- **의존성 스캔**: `pip audit`이나 `snyk` 등을 통해 취약점이 발견된 라이브러리를 사용하고 있지 않은가?

## 5. API 보안
- **Rate Limiting**: 무차별 대입 공격(Brute-force)이나 DoS 공격을 방지하기 위한 API 요청 제한이 설정되었는가?
- **CORS 설정**: 허용되지 않은 도메인에서의 리소스 접근을 차단하도록 CORS 정책을 보수적으로 설정했는가?

## 명령어 실행 전
- 실행할 명령어와 그 목적을 먼저 설명할 것
- 부작용이 있을 수 있는 경우 미리 알릴 것

## 일반 원칙
- 항상 "왜"를 먼저 설명하고 "무엇을" 할지 제안할 것
- 사용자 확인 없이 파일 수정이나 명령어 실행하지 말 것

---

## Django 코드 작성 규칙

### 객체 지향 설계 원칙

#### View/APIView 작성 시
- 단일 책임 원칙(SRP): 하나의 View는 하나의 리소스/기능만 담당
- 공통 로직은 Mixin 또는 Base 클래스로 분리
- 비즈니스 로직은 Service 레이어로 분리

```python
# 비즈니스 로직은 Service 클래스로 분리
class UserService:
    """사용자 관련 비즈니스 로직을 처리하는 서비스 클래스."""
    
    @staticmethod
    def get_active_users():
        return User.objects.filter(is_active=True)

# View는 요청/응답 처리만 담당
class UserListAPIView(APIView):
    """활성 사용자 목록을 조회하는 API."""
    
    def get(self, request):
        users = UserService.get_active_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
```

#### 상속 구조 활용
```python
class BaseAPIView(APIView):
    """모든 API View의 기본 클래스."""
    
    def handle_exception(self, exc):
        # 공통 예외 처리 로직
        pass

class UserAPIView(BaseAPIView):
    """사용자 API의 기본 클래스."""
    permission_classes = [IsAuthenticated]
```

### Docstring 작성 규칙 (Google Style)

#### 함수/메서드
```python
def calculate_total_price(items: list, discount: float = 0.0) -> float:
    """주문 항목들의 총 가격을 계산합니다.

    Args:
        items: 주문 항목 리스트. 각 항목은 'price' 키를 포함해야 함.
        discount: 적용할 할인율 (기본값: 0.0).

    Returns:
        할인이 적용된 총 가격.

    Raises:
        ValueError: 할인율이 0.0 ~ 1.0 범위를 벗어난 경우.
    """
    if not 0.0 <= discount <= 1.0:
        raise ValueError("할인율은 0.0 ~ 1.0 사이여야 합니다.")
    
    total = sum(item['price'] for item in items)
    return total * (1 - discount)
```

#### 클래스
```python
class OrderService:
    """주문 처리를 담당하는 서비스 클래스.

    주문 생성, 수정, 취소 등의 비즈니스 로직을 처리합니다.

    Attributes:
        order_repository: 주문 데이터 접근 객체.
        payment_service: 결제 처리 서비스.
    """
    
    def __init__(self, order_repository=None, payment_service=None):
        """OrderService를 초기화합니다.

        Args:
            order_repository: 주문 저장소 (기본값: OrderRepository()).
            payment_service: 결제 서비스 (기본값: PaymentService()).
        """
        self.order_repository = order_repository or OrderRepository()
        self.payment_service = payment_service or PaymentService()
```

#### APIView
```python
class OrderCreateAPIView(APIView):
    """새로운 주문을 생성하는 API.

    Endpoint:
        POST /api/orders/

    Request Body:
        - items (list): 주문 항목 리스트
        - shipping_address (str): 배송 주소

    Response:
        201 Created: 주문 생성 성공
        400 Bad Request: 유효하지 않은 요청 데이터
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """새로운 주문을 생성합니다.

        Args:
            request: HTTP 요청 객체.

        Returns:
            Response: 생성된 주문 정보와 201 상태 코드.
        """
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService().create_order(
            user=request.user,
            **serializer.validated_data
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
```

### Type Hints 사용
```python
from typing import Optional, List, Dict, Any

def get_user_orders(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """사용자의 주문 목록을 조회합니다."""
    pass
```

---

## React 코드 작성 규칙

### 컴포넌트 구조

#### 단일 책임 원칙
- 하나의 컴포넌트는 하나의 역할만 담당
- 컴포넌트가 200줄을 넘으면 분리 고려

```jsx
// ❌ Bad: 여러 책임이 혼재
function UserPage() {
  // 데이터 fetching, 폼 처리, 리스트 렌더링 모두 포함
}

// ✅ Good: 책임 분리
function UserPage() {
  return (
    <div>
      <UserSearchForm onSearch={handleSearch} />
      <UserList users={users} />
      <Pagination {...paginationProps} />
    </div>
  );
}
```

#### 컴포넌트 파일 구조
```
components/
├── common/              # 공통 컴포넌트
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.module.css
│   │   └── index.js
│   └── Modal/
├── features/            # 기능별 컴포넌트
│   ├── user/
│   │   ├── UserList.jsx
│   │   ├── UserForm.jsx
│   │   └── hooks/
│   │       └── useUser.js
│   └── order/
└── layout/              # 레이아웃 컴포넌트
    ├── Header.jsx
    └── Sidebar.jsx
```

### 네이밍 컨벤션

```jsx
// 컴포넌트: PascalCase
function UserProfileCard() {}

// 훅: use 접두사 + camelCase
function useUserData() {}

// 이벤트 핸들러: handle 접두사
const handleSubmit = () => {};
const handleUserClick = () => {};

// props로 전달되는 핸들러: on 접두사
<Button onClick={handleClick} onHover={handleHover} />

// boolean props: is, has, can 접두사
<Modal isOpen={isOpen} hasError={hasError} canClose={canClose} />

// 상수: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = '/api/v1';
```

### JSDoc 주석 작성

#### 컴포넌트
```jsx
/**
 * 사용자 정보를 카드 형태로 표시하는 컴포넌트
 * 
 * @param {Object} props
 * @param {Object} props.user - 사용자 정보 객체
 * @param {string} props.user.name - 사용자 이름
 * @param {string} props.user.email - 사용자 이메일
 * @param {boolean} [props.isEditable=false] - 수정 가능 여부
 * @param {Function} [props.onEdit] - 수정 버튼 클릭 핸들러
 * @returns {JSX.Element}
 * 
 * @example
 * <UserCard 
 *   user={{ name: '홍길동', email: 'hong@example.com' }}
 *   isEditable={true}
 *   onEdit={handleEdit}
 * />
 */
function UserCard({ user, isEditable = false, onEdit }) {
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      {isEditable && <button onClick={onEdit}>수정</button>}
    </div>
  );
}
```

#### Custom Hook
```jsx
/**
 * 사용자 데이터를 관리하는 커스텀 훅
 * 
 * @param {number} userId - 조회할 사용자 ID
 * @returns {Object} 사용자 데이터 및 상태
 * @returns {Object|null} returns.user - 사용자 정보
 * @returns {boolean} returns.isLoading - 로딩 상태
 * @returns {Error|null} returns.error - 에러 객체
 * @returns {Function} returns.refetch - 데이터 재조회 함수
 * 
 * @example
 * const { user, isLoading, error, refetch } = useUser(1);
 */
function useUser(userId) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // ...

  return { user, isLoading, error, refetch };
}
```

#### 유틸리티 함수
```jsx
/**
 * 날짜를 한국어 형식으로 포맷팅
 * 
 * @param {Date|string} date - 포맷팅할 날짜
 * @param {Object} [options] - 포맷 옵션
 * @param {boolean} [options.includeTime=false] - 시간 포함 여부
 * @returns {string} 포맷팅된 날짜 문자열
 * 
 * @example
 * formatDate('2024-01-15') // '2024년 1월 15일'
 * formatDate('2024-01-15', { includeTime: true }) // '2024년 1월 15일 오후 3:30'
 */
function formatDate(date, options = {}) {
  // ...
}
```

### 코드 구성 순서

컴포넌트 내부 코드는 다음 순서로 작성:

```jsx
function UserForm({ initialData, onSubmit }) {
  // 1. 상태 선언 (useState)
  const [formData, setFormData] = useState(initialData);
  const [errors, setErrors] = useState({});

  // 2. ref 선언 (useRef)
  const inputRef = useRef(null);

  // 3. 컨텍스트 (useContext)
  const { theme } = useContext(ThemeContext);

  // 4. 커스텀 훅
  const { user } = useUser();

  // 5. 파생 상태 (useMemo)
  const isValid = useMemo(() => {
    return formData.name && formData.email;
  }, [formData]);

  // 6. 이펙트 (useEffect)
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // 7. 이벤트 핸들러
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  // 8. 렌더링 헬퍼 함수
  const renderError = (field) => {
    return errors[field] && <span className="error">{errors[field]}</span>;
  };

  // 9. 조건부 렌더링 (early return)
  if (!user) {
    return <Loading />;
  }

  // 10. 메인 렌더링
  return (
    <form onSubmit={handleSubmit}>
      {/* ... */}
    </form>
  );
}
```

### Props 처리

```jsx
// Props 기본값은 구조분해에서 설정
function Button({ 
  children,
  variant = 'primary',
  size = 'medium',
  isDisabled = false,
  onClick,
}) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={isDisabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// props 전달 시 spread 보다 명시적 전달 선호
// ❌ Bad
<UserCard {...userData} />

// ✅ Good
<UserCard 
  name={userData.name}
  email={userData.email}
  role={userData.role}
/>
```

### API 호출 패턴

```jsx
// services/api/userApi.js
/**
 * 사용자 API 모듈
 */
const userApi = {
  /**
   * 사용자 목록 조회
   * @param {Object} params - 조회 파라미터
   * @returns {Promise<Array>}
   */
  getUsers: async (params) => {
    const response = await apiClient.get('/users', { params });
    return response.data;
  },

  /**
   * 사용자 생성
   * @param {Object} userData - 생성할 사용자 데이터
   * @returns {Promise<Object>}
   */
  createUser: async (userData) => {
    const response = await apiClient.post('/users', userData);
    return response.data;
  },
};

export default userApi;
```
