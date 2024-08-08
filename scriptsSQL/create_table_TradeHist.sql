USE [TradeDB]
GO

CREATE TABLE [dbo].[TradeHist](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[CoinName] [varchar](20) NULL,
	[Type] [char](20) NULL,
	[RsiBtc] [float] NULL,
	[RsiCoin] [float] NULL,
	[Reveserd] [char](10) NULL,
	[volUSDT] [char](20) NULL,
	[DifPercent] [float] NULL,
	[OrderRole] [int] NULL,
	[GainPercent] [float] NULL,
	[LossPercent] [float] NULL,
	[BotInfo] [char](20) NULL,
	[ReturnUsdt] [float] NULL,
	[Created] [smalldatetime] NULL,
	[Ended] [smalldatetime] NULL,
	[TransactionId] [uniqueidentifier] NULL,
	[RsiCoinOut] [float] NULL,
	[rsiBTCOut] [float] NULL,
	[roleType] [char](100) NULL,
	[roleType2] [char](250) NULL,
PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


