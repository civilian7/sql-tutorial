-- Add comments to tutorial.db
CREATE TABLE IF NOT EXISTS _sc_metadata (
    type TEXT, name TEXT, subname TEXT, comment TEXT,
    PRIMARY KEY (type, name, subname)
);

-- Table comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'customers', '', '고객 마스터. 등급(BRONZE/SILVER/GOLD/VIP), 적립금, 가입채널, 활성상태 관리');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'customer_addresses', '', '고객 배송지. 고객당 복수 주소, 기본 배송지 지정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'categories', '', '상품 카테고리. 대/중/소 3단계 계층(self-referencing FK)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'suppliers', '', '공급업체(입점 판매자). 사업자 정보, 담당자 연락처 관리');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'products', '', '상품 마스터. SKU, 판매가/원가, 재고, 브랜드/모델, 후속상품 관리');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_images', '', '상품 이미지. 상품당 복수 이미지(메인/상세/라이프스타일 등)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_prices', '', '상품 가격 이력. 가격 변경 시 트리거 자동 기록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'orders', '', '주문. 주문번호(ORD-YYYYMMDD-NNNNN), 상태 흐름(pending→delivered/cancelled)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'order_items', '', '주문 상세 항목. 주문 시점 단가/수량, 아이템별 할인');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'payments', '', '결제. 카드/계좌이체/간편결제, PG 거래번호, 현금영수증');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'shipping', '', '배송. 택배사, 운송장번호, 배송 상태 추적');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'returns', '', '반품/교환. 사유, 검수 결과, 환불 상태, 수거 택배 정보');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'reviews', '', '상품 리뷰. 1~5점 별점, 구매 인증 여부');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'carts', '', '장바구니. active/converted/abandoned 상태 관리');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'cart_items', '', '장바구니 항목. 담긴 상품과 수량');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'coupons', '', '쿠폰 정의. 정률/정액 할인, 사용 한도, 유효기간');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'coupon_usage', '', '쿠폰 사용 이력. 고객-주문-쿠폰 매핑');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'complaints', '', '고객 문의/불만. 카테고리별 분류, 우선순위, CS 담당자 배정, 보상 관리');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'inventory_transactions', '', '재고 변동 이력. 입고/출고/반품/조정 트랜잭션');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'staff', '', '내부 직원. 부서(sales/CS/logistics 등), 역할(admin/manager/staff), 조직도');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'wishlists', '', '위시리스트. 고객-상품 UNIQUE, 가격 하락 알림 설정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'calendar', '', '날짜 차원 테이블. 요일, 공휴일, 분기 등 날짜 속성');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'customer_grade_history', '', '고객 등급 변경 이력(SCD Type 2). 변경 전후 등급, 변경 사유');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'point_transactions', '', '포인트 적립/사용/소멸 원장. 거래 유형별 증감, 잔액 추적');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_qna', '', '상품 Q&A. 질문-답변 자기참조 스레드');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_tags', '', '상품-태그 연결(M:N). 복합 PK');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'product_views', '', '상품 조회 로그. 유입경로, 기기유형, 체류시간 기록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'promotion_products', '', '프로모션 대상 상품. 프로모션-상품 연결(M:N), 특가 설정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'promotions', '', '프로모션/세일 이벤트. 할인율/금액, 기간, 대상 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('table', 'tags', '', '상품 태그 마스터. 태그명, 분류(feature/use_case/target/spec)');

-- Columns: customers
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'id', 'PK. 자동증가. 고객 고유 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'email', 'UNIQUE. 이메일 주소. 로그인 ID');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'password_hash', 'NOT NULL. SHA-256 비밀번호 해시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'name', 'NOT NULL. 고객 실명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'phone', 'NOT NULL. 020-XXXX-XXXX 형식. 연락처');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'birth_date', 'YYYY-MM-DD. 생년월일. NULL=미입력(약 15%)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'gender', 'ENUM(M,F). 성별. NULL=미입력(약 10%)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'grade', 'ENUM(BRONZE,SILVER,GOLD,VIP). 구매 실적 기반 회원 등급. 분기별 재산정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'point_balance', '정수 ≥0. 보유 적립금');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'is_active', '0/1. 활성=1, 탈퇴=0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'last_login_at', 'YYYY-MM-DD HH:MM:SS. 마지막 로그인 일시. NULL=미접속');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'created_at', 'YYYY-MM-DD HH:MM:SS. 가입 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신');

-- Columns: products
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'id', 'PK. 자동증가. 상품 고유 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'category_id', 'FK→categories(id). NOT NULL. 소속 카테고리');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'supplier_id', 'FK→suppliers(id). NOT NULL. 공급업체');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'name', 'NOT NULL. 상품명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'sku', 'UNIQUE. NOT NULL. 재고관리코드');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'brand', 'NOT NULL. 브랜드명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'model_number', '제조사 모델번호. NULL=미등록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'description', '상품 설명. NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'price', 'DECIMAL ≥0. 현재 판매가(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'cost_price', 'DECIMAL ≥0. 원가(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'stock_qty', '정수. 현재 재고 수량. 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'weight_grams', '정수. 배송 무게(그램). NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'is_active', '0/1. 판매중=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'discontinued_at', 'YYYY-MM-DD HH:MM:SS. 단종일. NULL=판매중');

-- Columns: orders
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'id', 'PK. 자동증가. 주문 고유 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'order_number', 'UNIQUE. ORD-YYYYMMDD-NNNNN 형식. 주문번호');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'customer_id', 'FK→customers(id). NOT NULL. 주문한 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'address_id', 'FK→customer_addresses(id). 배송지');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'staff_id', 'FK→staff(id). CS 담당 직원. NULL=미배정(취소/반품 시 배정)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'status', 'ENUM(pending,paid,preparing,shipped,delivered,confirmed,cancelled). 주문 상태');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'total_amount', 'DECIMAL. 최종 결제 금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'discount_amount', 'DECIMAL. 할인 합계. 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'shipping_fee', 'DECIMAL. 배송비. 5만원 이상 무료');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'point_used', '정수. 사용한 적립금. 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'point_earned', '정수. 적립 예정 포인트. 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'notes', '배송 메모. NULL=메모 없음');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'ordered_at', 'YYYY-MM-DD HH:MM:SS. 주문 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'completed_at', 'YYYY-MM-DD HH:MM:SS. 구매확정일. NULL=미확정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'cancelled_at', 'YYYY-MM-DD HH:MM:SS. 취소일. NULL=취소 안 됨');

-- Columns: order_items
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'order_id', 'FK→orders(id). NOT NULL. 소속 주문');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'product_id', 'FK→products(id). NOT NULL. 주문 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'quantity', '정수 ≥1. 주문 수량');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'unit_price', 'DECIMAL. 주문 시점 단가(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'discount_amount', 'DECIMAL. 아이템별 할인 금액. 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'subtotal', 'DECIMAL. 소계 = (단가 × 수량) - 할인');

-- Columns: payments
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'method', 'ENUM(card,bank_transfer,kakao_pay,naver_pay,point). 결제 수단');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'amount', 'DECIMAL. 결제 금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'status', 'ENUM(pending,completed,failed,refunded). 결제 상태');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'pg_transaction_id', 'PG사 거래번호. NULL=미발급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'card_issuer', '카드사(신한/삼성/KB국민/현대 등). NULL=카드 외 결제');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'installment_months', '정수. 할부 개월수. 0=일시불');

-- Columns: returns
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'return_type', 'ENUM(refund,exchange). 반품 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'reason', 'ENUM(defective,wrong_item,change_of_mind,damaged_in_transit,not_as_described,late_delivery). 반품 사유');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'status', 'ENUM(requested,pickup_scheduled,in_transit,completed). 반품 상태');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'is_partial', '0/1. 부분반품=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'inspection_result', 'ENUM(good,opened_good,defective,unsellable). 검수 결과. NULL=미검수');

-- Columns: reviews
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'rating', '범위 1~5. 별점');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'is_verified', '0/1. 구매인증=1');

-- Columns: coupons
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'code', 'UNIQUE. 쿠폰 코드');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'type', 'ENUM(percent,fixed). percent=정률, fixed=정액');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'discount_value', 'DECIMAL. 할인율(%) 또는 할인금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'min_order_amount', 'DECIMAL. 최소 주문금액 조건');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'max_discount', 'DECIMAL. 최대 할인금액(정률 시 상한). NULL=제한 없음');

-- Columns: complaints
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'category', 'ENUM(product_defect,delivery_issue,wrong_item,refund_request,exchange_request,general_inquiry,price_inquiry). 문의 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'channel', 'ENUM(website,phone,email,chat,kakao). 접수 채널');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'priority', 'ENUM(low,medium,high,urgent). 우선순위');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'status', 'ENUM(open,resolved,closed). 처리 상태');

-- Columns: inventory_transactions
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'type', 'ENUM(inbound,outbound,return,adjustment). 변동 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'quantity', '정수. 양수=입고, 음수=출고');

-- Columns: categories
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'parent_id', 'FK→categories(id). 상위 카테고리. NULL=최상위');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'depth', '범위 0~2. 0=대분류, 1=중분류, 2=소분류');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'slug', 'UNIQUE. URL용 식별자');

-- Columns: shipping
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'carrier', 'CJ대한통운/한진택배/로젠택배/우체국택배. 택배사');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'tracking_number', '운송장 번호. NULL=미발급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'status', 'ENUM(preparing,shipped,in_transit,delivered,returned). 배송 상태');

-- Columns: wishlists
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'notify_on_sale', '0/1. 가격 하락 알림=1');

-- Index comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_customers_email', '', 'customers.email. 로그인 시 이메일 검색');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_customer_id', '', 'orders.customer_id. 고객별 주문 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_ordered_at', '', 'orders.ordered_at. 주문일 범위 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_order_number', '', 'orders.order_number. 주문번호 CS 검색');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_status', '', 'orders.status. 주문 상태별 필터링');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_orders_customer_status', '', 'orders.(customer_id,status). 마이페이지 복합 인덱스');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_category_id', '', 'products.category_id. 카테고리별 상품 목록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_name', '', 'products.name. 상품명 검색');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_sku', '', 'products.sku. SKU 코드 검색(재고 관리)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_products_supplier_id', '', 'products.supplier_id. 공급업체별 상품 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_order_items_order_id', '', 'order_items.order_id. 주문별 상세 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_order_items_product_id', '', 'order_items.product_id. 상품별 판매 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_order_items_order_product', '', 'order_items.(order_id,product_id). 중복 체크 복합 인덱스');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_reviews_product_id', '', 'reviews.product_id. 상품별 리뷰 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_reviews_product_rating', '', 'reviews.(product_id,rating). 별점 필터 복합 인덱스');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_reviews_customer_id', '', 'reviews.customer_id. 고객별 리뷰 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_order_id', '', 'returns.order_id. 주문별 반품 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_reason', '', 'returns.reason. 반품 사유별 통계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_status', '', 'returns.status. 반품 상태별 필터링');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_returns_customer_id', '', 'returns.customer_id. 고객별 반품 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_category', '', 'complaints.category. 문의 유형별 통계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_status', '', 'complaints.status. 문의 상태별 필터링');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_customer_id', '', 'complaints.customer_id. 고객별 문의 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_order_id', '', 'complaints.order_id. 주문별 문의 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_complaints_staff_id', '', 'complaints.staff_id. 담당 직원별 문의');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_payments_order_id', '', 'payments.order_id. 주문별 결제 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_shipping_order_id', '', 'shipping.order_id. 주문별 배송 조회');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_carts_customer_id', '', 'carts.customer_id. 고객별 장바구니');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_cart_items_cart_id', '', 'cart_items.cart_id. 장바구니별 항목');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_coupon_usage_coupon_id', '', 'coupon_usage.coupon_id. 쿠폰별 사용 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_coupon_usage_customer_id', '', 'coupon_usage.customer_id. 고객별 쿠폰 사용');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_coupon_usage_order_id', '', 'coupon_usage.order_id. 주문별 쿠폰 사용');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_customer_addresses_customer_id', '', 'customer_addresses.customer_id. 고객별 배송지 목록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_inventory_product_id', '', 'inventory_transactions.product_id. 상품별 재고 변동 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_product_images_product_id', '', 'product_images.product_id. 상품별 이미지 목록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_product_prices_product_id', '', 'product_prices.product_id. 상품별 가격 이력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_wishlists_customer_id', '', 'wishlists.customer_id. 고객별 위시리스트');
INSERT OR REPLACE INTO _sc_metadata VALUES ('index', 'idx_wishlists_product_id', '', 'wishlists.product_id. 상품별 위시리스트 수');

-- View comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_customer_summary', '', '고객 요약. 총주문/총매출/평균주문액/첫주문일/최근주문일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_customer_rfm', '', '고객 RFM 분석. Recency/Frequency/Monetary 세그먼트');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_order_detail', '', '주문 상세. 주문+고객+상품+결제 정보 조인');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_daily_orders', '', '일별 주문 통계. 주문수/매출/평균단가/신규고객수');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_monthly_sales', '', '월별 매출 통계. 매출/주문수/고객수/평균단가');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_yearly_kpi', '', '연간 KPI. 매출/주문수/고객수/객단가/반품률/리뷰평점');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_product_performance', '', '상품별 실적. 판매량/매출/리뷰수/평균별점/마진율');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_product_abc', '', '상품 ABC 분석. 매출 기여도별 A/B/C 등급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_category_tree', '', '카테고리 계층. 대>중>소 전체 경로');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_top_products_by_category', '', '카테고리별 TOP 3 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_supplier_performance', '', '공급업체별 실적. 상품수/매출/반품률');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_payment_summary', '', '결제 수단별 통계. 건수/금액/비율');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_return_analysis', '', '반품 분석. 사유별/유형별/상태별 통계');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_revenue_growth', '', '매출 성장률. 월별 전월 대비 증감');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_hourly_pattern', '', '시간대별 주문 패턴');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_coupon_effectiveness', '', '쿠폰 효과 분석. 사용률/평균할인/매출 기여');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_cart_abandonment', '', '장바구니 이탈 분석. 이탈률/평균금액');
INSERT OR REPLACE INTO _sc_metadata VALUES ('view', 'v_staff_workload', '', '직원별 업무량. 담당 주문수/문의수/처리 시간');

-- Trigger comments
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_customers_updated_at', '', 'customers. UPDATE 시 updated_at 자동 갱신');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_orders_updated_at', '', 'orders. UPDATE 시 updated_at 자동 갱신');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_products_updated_at', '', 'products. UPDATE 시 updated_at 자동 갱신');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_product_price_history', '', 'products. 가격 변경 시 product_prices에 이력 자동 기록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('trigger', 'trg_reviews_updated_at', '', 'reviews. UPDATE 시 updated_at 자동 갱신');

-- Columns: calendar
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'date_key', 'PK. YYYY-MM-DD 형식. 날짜 키');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'year', '정수. 연도(예: 2024)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'month', '범위 1~12. 월');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'day', '범위 1~31. 일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'quarter', '범위 1~4. 분기');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'day_of_week', '범위 0~6. 0=월요일, 6=일요일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'day_name', 'Monday~Sunday. 요일명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'is_weekend', '0/1. 주말=1(토/일)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'is_holiday', '0/1. 공휴일=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'calendar', 'holiday_name', '공휴일명. NULL=공휴일 아님');

-- Columns: cart_items
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'cart_items', 'id', 'PK. 자동증가. 장바구니 항목 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'cart_items', 'cart_id', 'FK→carts(id). NOT NULL. 소속 장바구니');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'cart_items', 'product_id', 'FK→products(id). NOT NULL. 담은 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'cart_items', 'quantity', '정수 ≥1. 담은 수량. 기본값 1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'cart_items', 'added_at', 'YYYY-MM-DD HH:MM:SS. 장바구니 담은 일시');

-- Columns: carts
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'carts', 'id', 'PK. 자동증가. 장바구니 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'carts', 'customer_id', 'FK→customers(id). NOT NULL. 소유 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'carts', 'status', 'ENUM(active,converted,abandoned). 장바구니 상태');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'carts', 'created_at', 'YYYY-MM-DD HH:MM:SS. 생성 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'carts', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시');

-- Columns: categories (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'id', 'PK. 자동증가. 카테고리 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'name', 'NOT NULL. 카테고리명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'sort_order', '정수. 표시 순서(오름차순)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'is_active', '0/1. 활성=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'categories', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시');

-- Columns: complaints (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'id', 'PK. 자동증가. 문의/클레임 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'order_id', 'FK→orders(id). 관련 주문. NULL=일반문의');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'customer_id', 'FK→customers(id). NOT NULL. 문의 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'staff_id', 'FK→staff(id). CS 담당 직원. NULL=미배정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'title', 'NOT NULL. 문의 제목');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'content', 'NOT NULL. 문의 내용');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'resolution', '처리 결과 상세. resolved 시 작성. NULL=미해결');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'type', 'ENUM(inquiry,claim,report). 문의 유형. 기본값 inquiry');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'sub_category', '세부 분류(initial_defect/in_use_damage/misdelivery 등). NULL=미지정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'compensation_type', 'ENUM(refund,exchange,partial_refund,point_compensation,none). 보상 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'compensation_amount', 'DECIMAL. 보상 금액(원). 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'escalated', '0/1. 상위 관리자 에스컬레이션=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'response_count', '정수. 응대 횟수. 기본값 1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'created_at', 'YYYY-MM-DD HH:MM:SS. 접수 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'resolved_at', 'YYYY-MM-DD HH:MM:SS. 해결 일시. NULL=미해결');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'complaints', 'closed_at', 'YYYY-MM-DD HH:MM:SS. 종료 일시. NULL=미종료');

-- Columns: coupon_usage
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupon_usage', 'id', 'PK. 자동증가. 쿠폰 사용 이력 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupon_usage', 'coupon_id', 'FK→coupons(id). NOT NULL. 사용 쿠폰');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupon_usage', 'customer_id', 'FK→customers(id). NOT NULL. 사용 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupon_usage', 'order_id', 'FK→orders(id). NOT NULL. 사용 주문');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupon_usage', 'discount_amount', 'DECIMAL. 실제 할인 금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupon_usage', 'used_at', 'YYYY-MM-DD HH:MM:SS. 쿠폰 사용 일시');

-- Columns: coupons (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'id', 'PK. 자동증가. 쿠폰 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'name', 'NOT NULL. 쿠폰명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'usage_limit', '정수. 전체 사용 한도. NULL=무제한');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'per_user_limit', '정수. 1인당 사용 한도. 기본값 1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'is_active', '0/1. 활성=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'started_at', 'YYYY-MM-DD HH:MM:SS. 유효기간 시작일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'expired_at', 'YYYY-MM-DD HH:MM:SS. 유효기간 종료일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'coupons', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');

-- Columns: customer_addresses
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'id', 'PK. 자동증가. 배송지 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'customer_id', 'FK→customers(id). NOT NULL. 소유 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'label', 'ENUM(home,office,other). 배송지 구분');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'recipient_name', 'NOT NULL. 수령인 이름');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'phone', 'NOT NULL. 수령인 연락처');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'zip_code', 'NOT NULL. 우편번호');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'address1', 'NOT NULL. 기본 주소');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'address2', '상세 주소. NULL=미입력');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'is_default', '0/1. 기본 배송지=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_addresses', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 수정 일시. NULL=미수정');

-- Columns: customer_grade_history
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_grade_history', 'id', 'PK. 자동증가. 등급 이력 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_grade_history', 'customer_id', 'FK→customers(id). NOT NULL. 대상 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_grade_history', 'old_grade', 'ENUM(BRONZE,SILVER,GOLD,VIP). 변경 전 등급. NULL=최초 가입');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_grade_history', 'new_grade', 'ENUM(BRONZE,SILVER,GOLD,VIP). NOT NULL. 변경 후 등급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_grade_history', 'changed_at', 'YYYY-MM-DD HH:MM:SS. 등급 변경 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customer_grade_history', 'reason', 'ENUM(signup,upgrade,downgrade,yearly_review). 변경 사유');

-- Columns: customers (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'customers', 'acquisition_channel', 'ENUM(organic,search_ad,social,referral,direct). 유입 경로. NULL=미확인');

-- Columns: inventory_transactions (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'id', 'PK. 자동증가. 재고 변동 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'product_id', 'FK→products(id). NOT NULL. 대상 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'reference_id', '관련 주문 ID. NULL=초기입고/조정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'notes', '비고(initial_stock/regular_inbound/return_inbound 등)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'inventory_transactions', 'created_at', 'YYYY-MM-DD HH:MM:SS. 변동 일시');

-- Columns: order_items (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'order_items', 'id', 'PK. 자동증가. 주문 항목 식별자');

-- Columns: orders (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'created_at', 'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'orders', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신');

-- Columns: payments (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'id', 'PK. 자동증가. 결제 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'order_id', 'FK→orders(id). NOT NULL. 소속 주문');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'card_approval_no', '8자리. 카드 승인번호. NULL=카드 외 결제');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'bank_name', '은행명. NULL=계좌이체/가상계좌 외');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'account_no', '가상계좌 번호. NULL=해당 없음');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'depositor_name', '입금자명. NULL=계좌이체 외');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'easy_pay_method', '간편결제 세부수단(카카오페이 잔액/연결카드 등). NULL=간편결제 외');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'receipt_type', '소득공제/지출증빙. 현금영수증 유형. NULL=미발급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'receipt_no', '현금영수증 번호. NULL=미발급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'paid_at', 'YYYY-MM-DD HH:MM:SS. 결제 완료 일시. NULL=미완료');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'refunded_at', 'YYYY-MM-DD HH:MM:SS. 환불 일시. NULL=환불 없음');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'payments', 'created_at', 'YYYY-MM-DD HH:MM:SS. 결제 레코드 생성 일시');

-- Columns: point_transactions
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'id', 'PK. 자동증가. 포인트 거래 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'customer_id', 'FK→customers(id). NOT NULL. 대상 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'order_id', 'FK→orders(id). 관련 주문. NULL=가입/소멸');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'type', 'ENUM(earn,use,expire). 거래 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'reason', 'ENUM(purchase,confirm,review,signup,use,expiry). 사유');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'amount', '정수. 양수=적립, 음수=사용/소멸');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'balance_after', '정수. 거래 후 잔여 포인트');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'expires_at', 'YYYY-MM-DD HH:MM:SS. 적립 포인트 만료일. NULL=사용/소멸 건');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'point_transactions', 'created_at', 'YYYY-MM-DD HH:MM:SS. 거래 일시');

-- Columns: product_images
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'id', 'PK. 자동증가. 이미지 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'product_id', 'FK→products(id). NOT NULL. 소속 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'image_url', 'NOT NULL. 이미지 경로/URL');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'file_name', 'NOT NULL. 파일명(예: 42_1.jpg)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'image_type', 'ENUM(main,angle,side,back,detail,package,lifestyle,accessory,size_comparison). 이미지 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'alt_text', '대체 텍스트(접근성용). NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'width', '정수. 이미지 가로(px). NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'height', '정수. 이미지 세로(px). NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'file_size', '정수. 파일 크기(bytes). NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'sort_order', '정수. 표시 순서. 기본값 1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'is_primary', '0/1. 대표 이미지=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_images', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');

-- Columns: product_prices
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_prices', 'id', 'PK. 자동증가. 가격 이력 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_prices', 'product_id', 'FK→products(id). NOT NULL. 대상 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_prices', 'price', 'DECIMAL. 해당 기간 판매가(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_prices', 'started_at', 'YYYY-MM-DD HH:MM:SS. 적용 시작일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_prices', 'ended_at', 'YYYY-MM-DD HH:MM:SS. 적용 종료일. NULL=현재 가격');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_prices', 'change_reason', 'ENUM(regular,promotion,price_drop,cost_increase). 변경 사유');

-- Columns: product_qna
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'id', 'PK. 자동증가. Q&A 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'product_id', 'FK→products(id). NOT NULL. 대상 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'customer_id', 'FK→customers(id). 질문 고객. NULL=직원 답변');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'staff_id', 'FK→staff(id). 답변 직원. NULL=고객 질문');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'parent_id', 'FK→product_qna(id). 부모 글. NULL=질문, 값 있으면=답변');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'content', 'NOT NULL. 질문 또는 답변 내용');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'is_answered', '0/1. 답변 완료=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_qna', 'created_at', 'YYYY-MM-DD HH:MM:SS. 작성 일시');

-- Columns: product_tags
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_tags', 'product_id', 'FK→products(id). 복합 PK. 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_tags', 'tag_id', 'FK→tags(id). 복합 PK. 태그');

-- Columns: product_views
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'id', 'PK. 자동증가. 조회 로그 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'customer_id', 'FK→customers(id). NOT NULL. 조회 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'product_id', 'FK→products(id). NOT NULL. 조회 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'referrer_source', 'ENUM(direct,search,ad,recommendation,social,email). 유입 경로');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'device_type', 'ENUM(desktop,mobile,tablet). 접속 기기');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'duration_seconds', '정수. 페이지 체류 시간(초)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'product_views', 'viewed_at', 'YYYY-MM-DD HH:MM:SS. 조회 일시');

-- Columns: products (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'successor_id', 'FK→products(id). 후속 상품(단종 시 대체). NULL=없음');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'specs', 'JSON. 상품 상세 스펙. NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'products', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신');

-- Columns: promotion_products
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotion_products', 'promotion_id', 'FK→promotions(id). 복합 PK. 프로모션');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotion_products', 'product_id', 'FK→products(id). 복합 PK. 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotion_products', 'override_price', 'DECIMAL. 특가. NULL=프로모션 할인율 적용');

-- Columns: promotions
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'id', 'PK. 자동증가. 프로모션 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'name', 'NOT NULL. 프로모션명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'type', 'ENUM(seasonal,flash,category). 프로모션 유형');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'discount_type', 'ENUM(percent,fixed). percent=정률, fixed=정액');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'discount_value', 'DECIMAL. 할인율(%) 또는 할인금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'min_order_amount', 'DECIMAL. 최소 주문금액 조건. NULL=조건 없음');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'started_at', 'YYYY-MM-DD HH:MM:SS. 프로모션 시작일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'ended_at', 'YYYY-MM-DD HH:MM:SS. 프로모션 종료일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'is_active', '0/1. 활성=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'promotions', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');

-- Columns: returns (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'id', 'PK. 자동증가. 반품 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'order_id', 'FK→orders(id). NOT NULL. 원 주문');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'customer_id', 'FK→customers(id). NOT NULL. 반품 요청 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'reason_detail', '반품 상세 사유 설명. NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'refund_amount', 'DECIMAL. 환불 금액(원)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'refund_status', 'ENUM(pending,refunded,exchanged,partial_refund). 환불 상태');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'carrier', '수거 택배사. NULL=미배정');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'tracking_number', '수거 운송장 번호. NULL=미발급');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'requested_at', 'YYYY-MM-DD HH:MM:SS. 반품 요청 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'pickup_at', 'YYYY-MM-DD HH:MM:SS. 수거 예정/완료 일시. NULL=미예약');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'received_at', 'YYYY-MM-DD HH:MM:SS. 물류센터 입고 일시. NULL=미입고');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'inspected_at', 'YYYY-MM-DD HH:MM:SS. 검수 완료 일시. NULL=미검수');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'completed_at', 'YYYY-MM-DD HH:MM:SS. 처리 완료 일시. NULL=미완료');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'claim_id', 'FK→complaints(id). 연결 클레임. NULL=CS 미연결');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'exchange_product_id', 'FK→products(id). 교환 상품. NULL=환불 건');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'restocking_fee', 'DECIMAL. 변심 반품 재입고 수수료. 기본값 0');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'returns', 'created_at', 'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시');

-- Columns: reviews (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'id', 'PK. 자동증가. 리뷰 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'product_id', 'FK→products(id). NOT NULL. 리뷰 대상 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'customer_id', 'FK→customers(id). NOT NULL. 작성 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'order_id', 'FK→orders(id). 구매 주문. NULL=비구매 리뷰');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'title', '리뷰 제목. NULL=미작성(약 20%)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'content', '리뷰 본문. NULL 가능');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'created_at', 'YYYY-MM-DD HH:MM:SS. 작성 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'reviews', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시. 트리거 자동 갱신');

-- Columns: shipping (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'id', 'PK. 자동증가. 배송 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'order_id', 'FK→orders(id). NOT NULL. 소속 주문');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'shipped_at', 'YYYY-MM-DD HH:MM:SS. 발송 일시. NULL=미발송');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'delivered_at', 'YYYY-MM-DD HH:MM:SS. 배송완료 일시. NULL=미배송');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'created_at', 'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'shipping', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시');

-- Columns: staff
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'id', 'PK. 자동증가. 직원 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'manager_id', 'FK→staff(id). 상위 관리자(Self-Join). NULL=최상위');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'email', 'UNIQUE. staffN@techshop-staff.kr 형식. 직원 이메일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'name', 'NOT NULL. 직원 이름');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'phone', 'NOT NULL. 연락처');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'department', 'ENUM(sales,logistics,CS,marketing,dev,management). 부서');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'role', 'ENUM(admin,manager,staff). 역할');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'is_active', '0/1. 재직=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'hired_at', 'YYYY-MM-DD. 입사일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'staff', 'created_at', 'YYYY-MM-DD HH:MM:SS. 레코드 생성 일시');

-- Columns: suppliers
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'id', 'PK. 자동증가. 공급업체 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'company_name', 'NOT NULL. 회사명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'business_number', 'NOT NULL. 사업자등록번호(가상 번호)');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'contact_name', 'NOT NULL. 담당자명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'phone', 'NOT NULL. 020-XXXX-XXXX 형식. 연락처');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'email', 'NOT NULL. 담당자 이메일');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'address', '사업장 주소. NULL=미등록');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'is_active', '0/1. 거래 활성=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'suppliers', 'updated_at', 'YYYY-MM-DD HH:MM:SS. 최종 수정 일시');

-- Columns: tags
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'tags', 'id', 'PK. 자동증가. 태그 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'tags', 'name', 'UNIQUE. NOT NULL. 태그명');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'tags', 'category', 'ENUM(feature,use_case,target,spec). 태그 분류');

-- Columns: wishlists (추가분)
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'id', 'PK. 자동증가. 위시리스트 식별자');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'customer_id', 'FK→customers(id). UNIQUE(customer_id,product_id). 고객');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'product_id', 'FK→products(id). UNIQUE(customer_id,product_id). 상품');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'is_purchased', '0/1. 구매 전환=1');
INSERT OR REPLACE INTO _sc_metadata VALUES ('column', 'wishlists', 'created_at', 'YYYY-MM-DD HH:MM:SS. 등록 일시');
