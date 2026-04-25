package com.example.fitbridge

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForwardIos
import androidx.compose.material.icons.automirrored.filled.Chat
import androidx.compose.material.icons.automirrored.filled.DirectionsRun
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.health.connect.client.HealthConnectClient
import java.text.SimpleDateFormat
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
import androidx.lifecycle.lifecycleScope
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.fitbridge.model.DataPoint
import com.example.fitbridge.ui.theme.FitBridgeTheme
import com.example.fitbridge.util.HealthReportGenerator
import com.example.fitbridge.worker.FitnessWorker
import kotlinx.coroutines.launch
import java.util.*
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity() {

    private lateinit var viewModel: FitnessViewModel
    private lateinit var healthConnectClient: HealthConnectClient

    private val permissions = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class)
    )

    private val requestPermissionLauncher = registerForActivityResult(
        PermissionController.createRequestPermissionResultContract()
    ) { granted ->
        if (granted.containsAll(permissions)) {
            startFitnessWork()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        healthConnectClient = HealthConnectClient.getOrCreate(this)
        val repository = FitnessRepository(this)
        viewModel = FitnessViewModel(repository, this)

        checkAndRequestHealthPermissions()

        setContent {
            FitBridgeTheme {
                MainContainer(viewModel)
            }
        }
    }

    private fun checkAndRequestHealthPermissions() {
        lifecycleScope.launch {
            val granted = healthConnectClient.permissionController.getGrantedPermissions()
            if (granted.containsAll(permissions)) {
                startFitnessWork()
            } else {
                requestPermissionLauncher.launch(permissions)
            }
        }
    }

    private fun startFitnessWork() {
        viewModel.startPolling()
        val workRequest = PeriodicWorkRequestBuilder<FitnessWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "FitnessDataSync",
            ExistingPeriodicWorkPolicy.KEEP,
            workRequest
        )
    }
}

@Composable
fun MainContainer(viewModel: FitnessViewModel) {
    var selectedTab by remember { mutableIntStateOf(0) }
    var showChatOverlay by remember { mutableStateOf(false) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .windowInsetsPadding(WindowInsets.systemBars.only(WindowInsetsSides.Horizontal + WindowInsetsSides.Top))
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            when (selectedTab) {
                0 -> AIHomePage(viewModel, onOpenChat = { showChatOverlay = true })
                1 -> ProgressPage(viewModel)
                2 -> RecommendationsPage(viewModel)
                3 -> PrescriptionPage(viewModel)
            }
        }

        // Floating Glassy Navigation Bar - Positioned above system nav
        if (!showChatOverlay) {
            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .windowInsetsPadding(WindowInsets.navigationBars)
                    .padding(bottom = 16.dp)
            ) {
                GlassyNavigationBar(
                    selectedTab = selectedTab,
                    onTabSelected = { selectedTab = it },
                    modifier = Modifier
                )
            }
        }

        // Dedicated Chat Overlay for better UX
        AnimatedVisibility(
            visible = showChatOverlay,
            enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
            exit = slideOutVertically(targetOffsetY = { it }) + fadeOut()
        ) {
            ChatOverlay(
                viewModel = viewModel,
                onClose = { showChatOverlay = false }
            )
        }
    }
}

@Composable
fun GlassyNavigationBar(selectedTab: Int, onTabSelected: (Int) -> Unit, modifier: Modifier) {
    Surface(
        modifier = modifier
            .padding(horizontal = 24.dp)
            .height(64.dp)
            .fillMaxWidth(),
        color = Color(0xDD000000), // Solid black glassy
        shape = RoundedCornerShape(32.dp),
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f)),
        shadowElevation = 8.dp
    ) {
        Row(
            modifier = Modifier.fillMaxSize(),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            NavIcon(Icons.Default.Terminal, "Home", selectedTab == 0) { onTabSelected(0) }
            NavIcon(Icons.Default.BarChart, "Stats", selectedTab == 1) { onTabSelected(1) }
            NavIcon(Icons.Default.Psychology, "AI Coach", selectedTab == 2) { onTabSelected(2) }
            NavIcon(Icons.Default.VerifiedUser, "Verdict", selectedTab == 3) { onTabSelected(3) }
        }
    }
}

@Composable
fun NavIcon(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, isSelected: Boolean, onClick: () -> Unit) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(CircleShape)
            .clickable { onClick() }
            .padding(8.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = if (isSelected) MaterialTheme.colorScheme.primary else Color.White.copy(alpha = 0.5f),
            modifier = Modifier.size(28.dp)
        )
        if (isSelected) {
            Box(modifier = Modifier.size(4.dp).clip(CircleShape).background(MaterialTheme.colorScheme.primary))
        }
    }
}

@Composable
fun AIHomePage(viewModel: FitnessViewModel, onOpenChat: () -> Unit) {
    val listState = rememberLazyListState()

    Column(modifier = Modifier.fillMaxSize()) {
        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            contentPadding = PaddingValues(24.dp)
        ) {
            item {
                // Dashboard Header
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.DirectionsRun,
                            contentDescription = "Logo",
                            tint = Color(0xFFA020F0), // Purple logo color
                            modifier = Modifier.size(32.dp)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "FITBRIDGE",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.ExtraBold,
                            color = Color.White
                        )
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (viewModel.isSyncing) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                color = MaterialTheme.colorScheme.primary,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        } else {
                            IconButton(
                                onClick = { viewModel.triggerManualSync() },
                                modifier = Modifier.size(24.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Sync,
                                    contentDescription = "Sync",
                                    tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.7f),
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                            Spacer(modifier = Modifier.width(4.dp))
                        }

                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(if (viewModel.syncStatus.contains("Failed")) Color.Red else MaterialTheme.colorScheme.primary)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = if (viewModel.isSyncing) "SYNCING..." else "LIVE STREAM",
                            style = MaterialTheme.typography.labelSmall,
                            color = if (viewModel.syncStatus.contains("Failed")) Color.Red else MaterialTheme.colorScheme.primary
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                Text(
                    text = "Smart Dashboard",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color.White.copy(alpha = 0.5f)
                )
                Text(
                    text = "AI-powered overview of your day",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.White.copy(alpha = 0.3f)
                )
                Spacer(modifier = Modifier.height(16.dp))

                // Context Card
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    color = Color.White.copy(alpha = 0.05f),
                    border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f))
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Text(
                            text = "CURRENT STATUS",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = viewModel.profilerAgentLog,
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                // Prominent Chat Action Card
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp)
                        .clickable { onOpenChat() },
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.primary, // Solid Neon Green for high visibility
                    border = BorderStroke(1.dp, Color.White.copy(alpha = 0.2f))
                ) {
                    Row(
                        modifier = Modifier.padding(20.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(Color.Black.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.Chat,
                                contentDescription = null,
                                tint = Color.Black,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Column {
                            Text(
                                "Chat with AI",
                                style = MaterialTheme.typography.titleMedium,
                                color = Color.Black,
                                fontWeight = FontWeight.ExtraBold
                            )
                            Text(
                                "Start a conversation with WatchAgent",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.Black.copy(alpha = 0.7f)
                            )
                        }
                        Spacer(modifier = Modifier.weight(1f))
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowForwardIos,
                            contentDescription = null,
                            tint = Color.Black.copy(alpha = 0.5f),
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(32.dp))

                if (viewModel.savedSessions.isNotEmpty()) {
                    Text(
                        text = "── RECENT SESSIONS ─────────────",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White.copy(alpha = 0.2f)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }

            items(viewModel.savedSessions) { session ->
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                        .clickable {
                            viewModel.loadSession(session)
                            onOpenChat()
                        },
                    color = Color.White.copy(alpha = 0.05f),
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f))
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                            Icon(Icons.Default.History, contentDescription = null, tint = Color.White.copy(alpha = 0.5f), modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(12.dp))
                            Text(
                                text = session.title,
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White,
                                maxLines = 1
                            )
                        }
                        IconButton(
                            onClick = { viewModel.savedSessions.remove(session) },
                            modifier = Modifier.size(24.dp)
                        ) {
                            Icon(Icons.Default.Close, contentDescription = "Remove", tint = Color.White.copy(alpha = 0.3f), modifier = Modifier.size(16.dp))
                        }
                    }
                }
            }

            item { Spacer(modifier = Modifier.height(100.dp)) }
        }
    }
}

@Composable
fun ChatOverlay(viewModel: FitnessViewModel, onClose: () -> Unit) {
    var textState by remember { mutableStateOf("") }
    val keyboardController = LocalSoftwareKeyboardController.current
    val listState = rememberLazyListState()

    LaunchedEffect(viewModel.chatMessages.size) {
        if (viewModel.chatMessages.isNotEmpty()) {
            listState.animateScrollToItem(viewModel.chatMessages.size - 1)
        }
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Chat Header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onClose) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = Color.White)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text("AGENT QUERY", style = MaterialTheme.typography.titleMedium, color = Color.White)
                Spacer(modifier = Modifier.weight(1f))
                if (viewModel.chatMessages.isNotEmpty()) {
                    TextButton(onClick = { viewModel.startNewChat() }) {
                        Text("CLEAR", color = MaterialTheme.colorScheme.primary)
                    }
                }
            }

            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(horizontal = 24.dp, vertical = 8.dp)
            ) {
                items(viewModel.chatMessages) { message ->
                    ChatBubble(message)
                }

                if (viewModel.isChatting) {
                    item {
                        Text("Thinking...", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary, modifier = Modifier.padding(start = 8.dp))
                    }
                }
                item { Spacer(modifier = Modifier.height(16.dp)) }
            }

            // Chat Input
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .windowInsetsPadding(WindowInsets.navigationBars.union(WindowInsets.ime))
                    .padding(24.dp),
                color = Color.White.copy(alpha = 0.05f),
                shape = RoundedCornerShape(24.dp),
                border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f))
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextField(
                        value = textState,
                        onValueChange = { textState = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("Ask anything...", style = MaterialTheme.typography.bodyMedium, color = Color.White.copy(alpha = 0.5f)) },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent,
                            cursorColor = MaterialTheme.colorScheme.primary,
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White
                        ),
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                        keyboardActions = KeyboardActions(onSend = {
                            if (textState.isNotBlank()) {
                                viewModel.sendMessage(textState)
                                textState = ""
                            }
                        })
                    )
                    IconButton(
                        onClick = {
                            if (textState.isNotBlank()) {
                                viewModel.sendMessage(textState)
                                textState = ""
                                keyboardController?.hide()
                            }
                        },
                        enabled = textState.isNotBlank() && !viewModel.isChatting
                    ) {
                        Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send", tint = MaterialTheme.colorScheme.primary)
                    }
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessage) {
    val isUser = message.isUser
    val alignment = if (isUser) Alignment.CenterEnd else Alignment.CenterStart
    val bgColor = if (isUser) MaterialTheme.colorScheme.primary.copy(alpha = 0.2f) else Color.White.copy(alpha = 0.05f)
    val shape = if (isUser) {
        RoundedCornerShape(20.dp, 20.dp, 4.dp, 20.dp)
    } else {
        RoundedCornerShape(20.dp, 20.dp, 20.dp, 4.dp)
    }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        contentAlignment = alignment
    ) {
        Surface(
            color = bgColor,
            shape = shape,
            border = BorderStroke(1.dp, if (isUser) MaterialTheme.colorScheme.primary.copy(alpha = 0.3f) else Color.White.copy(alpha = 0.1f)),
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Text(
                text = message.text,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
                style = MaterialTheme.typography.bodyMedium,
                color = Color.White
            )
        }
    }
}

@Composable
fun ProgressPage(viewModel: FitnessViewModel) {
    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("HEALTH STATS", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.ExtraBold, color = Color.White)
        Text("Detailed telemetry from your sensors", style = MaterialTheme.typography.labelSmall, color = Color.White.copy(alpha = 0.4f))
        Spacer(modifier = Modifier.height(24.dp))

        ChartContainer(
            title = "Heart Rate Telemetry",
            currentValue = "${viewModel.heartRate.toInt()} BPM",
            valueColor = MaterialTheme.colorScheme.error
        ) {
            LineChart(dataPoints = viewModel.heartRateHistory, color = MaterialTheme.colorScheme.error)
        }
        Spacer(modifier = Modifier.height(16.dp))
        ChartContainer(
            title = "Step Progression",
            currentValue = "${viewModel.steps} STEPS",
            valueColor = MaterialTheme.colorScheme.primary
        ) {
            BarChart(dataPoints = viewModel.stepHistory, color = MaterialTheme.colorScheme.primary)
        }
    }
}

@Composable
fun RecommendationsPage(viewModel: FitnessViewModel) {
    Column(modifier = Modifier.fillMaxSize().padding(24.dp)) {
        Text("AI COACH", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.ExtraBold, color = Color.White)
        Text("Personalized insights to improve your day", style = MaterialTheme.typography.labelSmall, color = Color.White.copy(alpha = 0.4f))
        Spacer(modifier = Modifier.height(24.dp))
        
        LazyColumn(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            items(viewModel.recommendations) { rec ->
                RecommendationCard(rec)
            }
        }
    }
}

@Composable
fun RecommendationCard(text: String) {
    var isExpanded by remember { mutableStateOf(false) }
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { isExpanded = !isExpanded }
            .animateContentSize(),
        shape = RoundedCornerShape(24.dp),
        color = Color.White.copy(alpha = 0.05f),
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f))
    ) {
        Row(modifier = Modifier.padding(20.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Star, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.width(16.dp))
            Text(
                text = text,
                style = MaterialTheme.typography.bodyLarge,
                color = Color.White,
                maxLines = if (isExpanded) Int.MAX_VALUE else 2,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
fun PrescriptionPage(viewModel: FitnessViewModel) {
    val context = androidx.compose.ui.platform.LocalContext.current
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("FINAL VERDICT", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.ExtraBold, color = Color.White)
        Text("The system's ultimate decision for you", style = MaterialTheme.typography.labelSmall, color = Color.White.copy(alpha = 0.4f))
        Spacer(modifier = Modifier.height(32.dp))

        Text("── ANALYSIS LOG ────────────────", style = MaterialTheme.typography.labelSmall, color = Color.White.copy(alpha = 0.3f))
        Spacer(modifier = Modifier.height(16.dp))

        DecisionLogItem("CONTEXT ANALYZER", viewModel.profilerAgentLog, Color.White.copy(alpha = 0.5f))
        DecisionLogItem("URGENCY MONITOR", viewModel.actionAgentLog, MaterialTheme.colorScheme.primary)
        DecisionLogItem("WISDOM ENGINE", viewModel.arbiterAgentLog, Color(0xFFA020F0)) // Purple

        Spacer(modifier = Modifier.height(24.dp))

        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.3f))
        ) {
            Column(modifier = Modifier.padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    "FINAL VERDICT",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary,
                    letterSpacing = 2.sp
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    viewModel.prescription,
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    color = Color.White
                )
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Button(
            onClick = { HealthReportGenerator.generatePdfReport(context, viewModel) },
            modifier = Modifier.fillMaxWidth().height(64.dp),
            shape = RoundedCornerShape(32.dp),
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
        ) {
            Text("GENERATE FULL REPORT", fontWeight = FontWeight.Bold)
        }
        
        Spacer(modifier = Modifier.height(120.dp))
    }
}

@Composable
fun DecisionLogItem(agent: String, log: String, color: Color) {
    Column(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)) {
        Text(agent, style = MaterialTheme.typography.labelSmall, color = color, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(4.dp))
        Surface(
            modifier = Modifier.fillMaxWidth(),
            color = Color.White.copy(alpha = 0.05f),
            shape = RoundedCornerShape(8.dp),
            border = BorderStroke(1.dp, Color.White.copy(alpha = 0.05f))
        ) {
            Text(
                text = log,
                modifier = Modifier.padding(12.dp),
                style = MaterialTheme.typography.bodySmall,
                color = Color.White.copy(alpha = 0.8f)
            )
        }
    }
}

// Chart Components (Reuse/Adjust from previous implementation)
@Composable
fun ChartContainer(
    title: String,
    currentValue: String = "",
    valueColor: Color = Color.White,
    content: @Composable () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(28.dp),
        color = Color.White.copy(alpha = 0.05f),
        border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f))
    ) {
        Column(modifier = Modifier.padding(24.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title.uppercase(),
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp,
                    color = Color.White.copy(alpha = 0.6f)
                )
                if (currentValue.isNotEmpty()) {
                    Text(
                        text = currentValue,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.ExtraBold,
                        color = valueColor
                    )
                }
            }
            Spacer(modifier = Modifier.height(20.dp))
            Box(modifier = Modifier.height(160.dp).fillMaxWidth()) {
                content()
            }
        }
    }
}

@Composable
fun LineChart(dataPoints: List<DataPoint>, color: Color) {
    if (dataPoints.isEmpty()) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text(
                "00 BPM",
                style = MaterialTheme.typography.headlineLarge,
                color = Color.White.copy(alpha = 0.1f),
                fontWeight = FontWeight.ExtraBold
            )
        }
        return
    }
    val maxVal = dataPoints.maxOf { it.value }.coerceAtLeast(100f)
    val minVal = dataPoints.minOf { it.value }.coerceAtMost(40f)
    val range = (maxVal - minVal).coerceAtLeast(1f)
    Canvas(modifier = Modifier.fillMaxSize()) {
        val width = size.width
        val height = size.height
        val spacing = width / (dataPoints.size.coerceAtLeast(2) - 1).toFloat()
        val path = Path()
        dataPoints.forEachIndexed { index, point ->
            val x = index * spacing
            val y = height - ((point.value - minVal) / range * height)
            if (index == 0) path.moveTo(x, y) else path.lineTo(x, y)
        }
        drawPath(path = path, color = color, style = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round))
    }
}

@Composable
fun BarChart(dataPoints: List<DataPoint>, color: Color) {
    if (dataPoints.isEmpty()) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text(
                "00 STEPS",
                style = MaterialTheme.typography.headlineLarge,
                color = Color.White.copy(alpha = 0.1f),
                fontWeight = FontWeight.ExtraBold
            )
        }
        return
    }
    val maxVal = dataPoints.maxOf { it.value }.coerceAtLeast(500f)
    Canvas(modifier = Modifier.fillMaxSize()) {
        val width = size.width
        val height = size.height
        val barWidth = (width / dataPoints.size) * 0.4f
        val spacing = (width / dataPoints.size)
        dataPoints.forEachIndexed { index, point ->
            val x = index * spacing + (spacing - barWidth) / 2
            val barHeight = (point.value / maxVal) * height
            drawRoundRect(color = color, topLeft = Offset(x, height - barHeight), size = androidx.compose.ui.geometry.Size(barWidth, barHeight), cornerRadius = androidx.compose.ui.geometry.CornerRadius(12.dp.toPx()))
        }
    }
}
